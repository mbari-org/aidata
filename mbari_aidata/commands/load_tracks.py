# mbari_aidata, Apache-2.0 license
# Filename: commands/load_tracks.py
# Description: Load tracks from a .tar.gz file with track data
import click
import tarfile
import tempfile
import json
import pandas as pd
from mbari_aidata import common_args
from pathlib import Path
from mbari_aidata.logger import create_logger_file, info, err, warn
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, init_api_project, get_version_id, find_box_type, find_media_type, find_state_type
from mbari_aidata.plugins.loaders.tator.localization import gen_spec as gen_localization_spec, load_bulk_boxes
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
from mbari_aidata.commands.embedding_rank import rank_tdwa_boxes_by_similarity
import tator  # type: ignore

from dataclasses import dataclass
import math
import numpy as np
from typing import Optional, Tuple, List

@click.command("tracks", help="Load tracks from a .tar.gz file with track data")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.dry_run
@common_args.version
@click.option("--input", type=Path, required=True, help=".tar.gz file containing track data")
@click.option("--max-num", type=int, help="Maximum number of localizations in tracks to load")
@click.option("--iou-threshold", type=float, default=0.3, help="Soft IOU threshold for merging adjacent tracks (default: 0.3)")
@click.option("--frame-gap", type=int, default=5, help="Maximum frame gap to consider for merging tracks (default: 5)")
@click.option("--compute-embeddings", is_flag=True, help="Compute embeddings and similarity ranking for TDWA boxes")
@click.option("--device", type=str, default="cpu", help="Device for embedding computation (cpu or cuda:X)")
@click.option("--video-dir", type=Path, help="Directory containing video files for embedding computation (videos should have .mov extension)")
def load_tracks(token: str, disable_ssl_verify: bool, config: str, version: str, input: Path, dry_run: bool, max_num: int, iou_threshold: float, frame_gap: int, compute_embeddings: bool, device: str, video_dir: Path) -> int:
    """Load tracks from a .tar.gz file with track data. Returns the number of tracks loaded."""

    try:
        create_logger_file("load_tracks")

        # Validate input file
        if not input.exists():
            err(f"Input file {input} does not exist")
            return 0

        if not input.suffix == ".gz" and not str(input).endswith(".tar.gz"):
            err(f"Input file {input} must be a .tar.gz file")
            return 0

        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project, disable_ssl_verify)
        version_id = get_version_id(api, tator_project, version)

        # Get all types and check configuration
        track_type = find_state_type(api, tator_project.id, "Track")
        box_type = find_box_type(api, tator_project.id, "Box")
        tdwa_box_type = find_box_type(api, tator_project.id, "TDWABox")
        video_type = find_media_type(api, tator_project.id, "Video")

        assert "box" in config_dict["tator"], "Missing required 'box' key in configuration file"
        assert "track_state" in config_dict["tator"], "Missing required 'track_state' key in configuration file"
        assert "tdwa_box" in config_dict["tator"], "Missing required 'tdwa_box' key in configuration file"

        # Validate VSS configuration if embeddings are to be computed
        if compute_embeddings:
            assert "vss" in config_dict, "Missing required 'vss' key in configuration file for embedding computation"
            assert "model" in config_dict["vss"], "Missing required 'vss.model' key in configuration file"
            assert video_dir is not None, "Video directory is required when computing embeddings"
            assert video_dir.exists(), f"Video directory {video_dir} does not exist"

        box_attributes = config_dict["tator"]["box"]["attributes"]
        track_attributes = config_dict["tator"]["track_state"]["attributes"]
        tdwa_box_attributes = config_dict["tator"]["tdwa_box"]["attributes"]
        assert tdwa_box_attributes is not None, f"No TDWABox attributes found in configuration file"

        assert version_id is not None, f"No version found in project {project}"
        assert box_type is not None, f"No box type found in project {project} for type Box"
        assert tdwa_box_type is not None, f"No TDWABox type found in project {project} for type TDWABox"
        assert track_type is not None, f"No state type found in project {project} for type Track"
        assert video_type is not None, f"No track type found in project {project} for type Video"

        info(f"Processing track data from {input}")

        # Compute embeddings and similarity ranking for TDWA boxes if requested
        if compute_embeddings:
            info("Computing embeddings and similarity ranking for TDWA boxes")

        # Extract the tar.gz file to a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            info(f"Extracting {input} to temporary directory {tmpdir}")

            with tarfile.open(input, "r:gz") as tar:
                tar.extractall(path=tmpdir)

            tmpdir_path = Path(tmpdir)

            # The parent directory name is the same as the tar.gz prefix
            # e.g., i2MAP_20250403T092817Z_1000m_F031_25-tracks.tar.gz
            # Extract the prefix from the input filename
            tar_prefix = input.stem.replace('.tar', '')
            track_dir = tmpdir_path / tar_prefix

            if not track_dir.exists():
                err(f"Expected directory {track_dir} not found in extracted archive")
                return 0

            # Look for detections.csv and metadata.json
            detections_csv = track_dir / "detections.csv"
            metadata_json = track_dir / "metadata.json"
            tracks_csv = track_dir / "tracks.csv"

            if not tracks_csv.exists():
                err(f"tracks.csv not found in {track_dir}")
                return 0

            if not detections_csv.exists():
                err(f"detections.csv not found in {track_dir}")
                return 0

            if not metadata_json.exists():
                warn(f"metadata.json not found in {track_dir}, continuing without metadata")
                metadata = {}
            else:
                with open(metadata_json, 'r') as f:
                    metadata = json.load(f)
                info(f"Loaded metadata: {metadata.get('video_name', 'unknown')}")

            # Read the tracks CSV
            df_tracks = pd.read_csv(tracks_csv)

            if len(df_tracks) == 0:
                warn("No tracks found in tracks.csv")
                return 0
            assert all(f in df_tracks.columns for f in
                       ['tracker_id', 'first_frame', 'last_frame']), "Missing required fields in tracks.csv"

            # Read the detections CSV
            info(f"Reading detections from {detections_csv}")
            df_boxes = pd.read_csv(detections_csv)

            if df_boxes.empty:
                warn(f"No detections found in {detections_csv}")
                return 0
            assert all(f in df_boxes.columns for f in
                       ['tracker_id', 'x', 'y', 'xx', 'xy', 'label', 'frame']), "Missing required fields in detections.csv"

            info(f"Found {len(df_boxes)} detections across {df_boxes['tracker_id'].nunique()} tracks")

            video_name = metadata.get('video_name', tar_prefix.replace('-tracks', '') + '.mp4')
            # For compatibility, if the video name ends with .mov, replace it with .mp4.
            # Note: The video file must already be uploaded as .mp4 format, even if the original filename was .mov.
            video_name = video_name.replace('.mov', '.mp4')
            video_width = metadata.get('video_width', 1920)
            video_height = metadata.get('video_height', 1080)

            # Query for the video media object
            info(f"Looking for video with name: {video_name}")
            media_list = api.get_media_list(project=tator_project.id, name=video_name)

            if len(media_list) == 0:
                err(f"No media found with name {video_name} in project {tator_project.name}.")
                err("Media must be loaded before tracks/localizations.")
                return 0

            media_id = media_list[0].id
            info(f"Found media ID: {media_id}")

            if dry_run:
                info(f"Dry run - would load {len(df_boxes)} localizations from {df_boxes['tracker_id'].nunique()} tracks into Tator")
                return 0

            # Create localization specs for all detections
            max_load = -1 if max_num is None else max_num

            # Load in bulk 1000 boxes at a time
            box_count = len(df_boxes)
            batch_size = min(1000, box_count)
            num_loaded_tracks = 0
            num_loaded_boxes = 0
            box_ids = []
            localization_ids = {}
            track_tdwa = {}
            for i in range(0, box_count, batch_size):
                df_batch = df_boxes[i:i + batch_size]
                specs = []
                for index, row in df_batch.iterrows():
                    obj = row.to_dict()
                    attributes = format_attributes(obj, box_attributes)
                    specs.append(
                        gen_localization_spec(
                            box=[obj["x"], obj["y"], obj["xx"], obj["xy"]],
                            version_id=version_id,
                            label=obj["label"],
                            width=video_width,
                            height=video_height,
                            attributes=attributes,
                            frame_number=obj["frame"],
                            type_id=box_type.id,
                            media_id=media_id,
                            project_id=tator_project.id,
                            normalize=False,  # Data is already normalized between 0-1 as specified in detections.csv
                        )
                    )
                    tracker_id = obj["tracker_id"]
                    if tracker_id not in localization_ids:
                        localization_ids[tracker_id] = []
                        track_tdwa[tracker_id] = TimeDecayWeightedAverage()

                    if 'score' not in obj:
                        obj['score'] = 1.0
                    track_tdwa[tracker_id].add(obj["label"], obj["score"], obj["frame"], index)

                # Truncate the boxes if the max number of boxes to load is set
                if 0 < max_load <= len(specs):
                    specs = specs[:max_load]

                box_ids_ = load_bulk_boxes(tator_project.id, api, specs)
                info(f"Loaded {len(box_ids_)} boxes of {box_count} into Tator")
                box_ids += box_ids_

                for tracker_id, box_id in zip(df_batch['tracker_id'], box_ids_):
                    if tracker_id not in localization_ids:
                        localization_ids[tracker_id] = []
                    localization_ids[tracker_id].append(box_id)

                # Update the number of boxes loaded and finish if the max number of boxes to load is set
                num_loaded_boxes += len(box_ids_)
                if 0 < max_load <= num_loaded_boxes:
                    break

            # Load tracks and compute best labels first
            track_info = {}  # tracker_id -> {best_label, score, best_frame, first_frame, last_frame, best_box}
            for tracker_id in track_tdwa:
                track = df_tracks[df_tracks['tracker_id'] == tracker_id]
                first_frame = track.iloc[0]['first_frame']
                last_frame = track.iloc[-1]['last_frame']
                # Get the time-decayed average prediction
                best_label, score, best_frame, df_row_index = track_tdwa[tracker_id].time_decay_average(last_frame)
                
                track_info[tracker_id] = {
                    "best_label": best_label,
                    "score": score,
                    "best_frame": best_frame,
                    "first_frame": first_frame,
                    "last_frame": last_frame,
                    "df_row_index": df_row_index,
                }
                info(f"Best label for tracker {tracker_id}: {best_label} with score {score} at frame {best_frame}")

            # Merge tracks within frame_gap frames with sufficient IOU
            # Sort tracks by first_frame to process them in order
            sorted_tracker_ids = sorted(track_info.keys(), key=lambda tid: track_info[tid]["first_frame"])
            merged_tracker_map = {}  # old_tracker_id -> new_tracker_id (for merged tracks)
            
            for i, tracker_id in enumerate(sorted_tracker_ids):
                # Skip if already merged into another track
                if tracker_id in merged_tracker_map:
                    continue
                    
                current_info = track_info[tracker_id]
                current_last_frame = current_info["last_frame"]
                current_label = current_info["best_label"]
                
                # Look for adjacent tracks that could be merged
                for j in range(i + 1, len(sorted_tracker_ids)):
                    next_tracker_id = sorted_tracker_ids[j]
                    
                    # Skip if already merged
                    if next_tracker_id in merged_tracker_map:
                        continue
                    
                    next_info = track_info[next_tracker_id]
                    next_first_frame = next_info["first_frame"]
                    next_label = next_info["best_label"]
                    
                    # Check if tracks are within frame_gap frames (ignore label matching)
                    frame_distance = next_first_frame - current_last_frame
                    if 1 <= frame_distance <= frame_gap:
                        
                        # Get the last bounding box of current track
                        current_last_box = df_boxes[
                            (df_boxes['tracker_id'] == tracker_id) & 
                            (df_boxes['frame'] == current_last_frame)
                        ]
                        
                        # Get the first bounding box of next track
                        next_first_box = df_boxes[
                            (df_boxes['tracker_id'] == next_tracker_id) & 
                            (df_boxes['frame'] == next_first_frame)
                        ]
                        
                        # Check if we have boxes at both frames
                        if not current_last_box.empty and not next_first_box.empty:
                            # Get bounding box coordinates
                            box1 = (
                                current_last_box.iloc[0]['x'],
                                current_last_box.iloc[0]['y'],
                                current_last_box.iloc[0]['xx'],
                                current_last_box.iloc[0]['xy']
                            )
                            box2 = (
                                next_first_box.iloc[0]['x'],
                                next_first_box.iloc[0]['y'],
                                next_first_box.iloc[0]['xx'],
                                next_first_box.iloc[0]['xy']
                            )
                            
                            # Calculate soft IOU
                            iou_value = soft_iou(box1, box2)
                            
                            # Only merge if IOU exceeds threshold
                            if iou_value >= iou_threshold:
                                info(f"Merging tracker {next_tracker_id} (label: {next_label}) into {tracker_id} (label: {current_label}), frames {current_last_frame}→{next_first_frame} (gap: {frame_distance}), soft IOU: {iou_value:.3f}")
                                
                                # Merge localizations from next_tracker_id into tracker_id
                                localization_ids[tracker_id].extend(localization_ids[next_tracker_id])
                                
                                # Update the last_frame for the merged track
                                track_info[tracker_id]["last_frame"] = next_info["last_frame"]
                                current_last_frame = next_info["last_frame"]
                                
                                # Update best_frame and score if next track has better score
                                if next_info["score"] > track_info[tracker_id]["score"]:
                                    track_info[tracker_id]["best_frame"] = next_info["best_frame"]
                                    track_info[tracker_id]["score"] = next_info["score"]
                                    # Update best_label to the higher score track
                                    track_info[tracker_id]["best_label"] = next_label
                                
                                # Mark next_tracker_id as merged
                                merged_tracker_map[next_tracker_id] = tracker_id
                            else:
                                info(f"Skipping merge of tracker {next_tracker_id} (label: {next_label}) into {tracker_id} (label: {current_label}), frames {current_last_frame}→{next_first_frame} (gap: {frame_distance}), soft IOU {iou_value:.3f} < threshold {iou_threshold}")
                    
                    # If beyond frame gap, break since tracks are sorted by first_frame
                    elif next_first_frame > current_last_frame + frame_gap:
                        break

            # Compute embeddings and similarity ranking for TDWA boxes if requested (before creating boxes)
            rankings = {}
            if compute_embeddings:
                info("Computing embeddings and similarity ranking for TDWA boxes")

                # Prepare TDWA box data for embedding computation
                tdwa_box_data = []
                for tracker_id in track_info:
                    if tracker_id in merged_tracker_map:
                        continue  # Skip merged tracks
                    info_data = track_info[tracker_id]
                    obj = df_boxes.iloc[info_data["df_row_index"]].to_dict()
                    tdwa_box_data.append({
                        'id': tracker_id,
                        'x': obj["x"],
                        'y': obj["y"],
                        'xx': obj["xx"],
                        'xy': obj["xy"],
                        'frame': info_data["best_frame"]
                    })

                # Compute rankings
                # Use .mov extension for video file in the specified video directory
                video_filename_mov = video_name.replace('.mp4', '.mov')
                video_path = video_dir / video_filename_mov
                assert video_path.exists(), f"Video file {video_path} does not exist"

                rankings = rank_tdwa_boxes_by_similarity(
                    tdwa_boxes=tdwa_box_data,
                    video_path=str(video_path),
                    fps=metadata.get('video_fps', 30.0),  # Default to 30 fps if not specified
                    video_width=video_width,
                    video_height=video_height,
                    config_dict=config_dict,
                    device=device
                )

                if rankings:
                    info(f"Computed similarity rankings for {len(rankings)} TDWA boxes")
                    # Log a summary of top similarities
                    for box_id, ranking in rankings.items():
                        if ranking:
                            top_similar = ranking[0]
                            info(f"Box {box_id}: most similar to {top_similar[0]} (similarity: {top_similar[1]:.3f})")
                else:
                    warn("No similarity rankings were computed")

            # Create tdwa_box specs for non-merged tracks
            tdwa_box_specs = []
            for tracker_id in track_info:
                if tracker_id in merged_tracker_map:
                    continue
                info_data = track_info[tracker_id]
                obj = df_boxes.iloc[info_data["df_row_index"]].to_dict()
                attributes = format_attributes(obj, tdwa_box_attributes)
                
                # Add similarity_score if rankings were computed
                if rankings and tracker_id in rankings:
                    ranking_list = rankings[tracker_id]
                    if ranking_list:
                        # Use the highest similarity score (to the most similar box)
                        attributes['similarity_score'] = float(ranking_list[0][1])
                    else:
                        attributes['similarity_score'] = 0.0
                else:
                    # No ranking available, set to 0 or None
                    attributes['similarity_score'] = 0.0
                
                tdwa_box_specs.append(gen_localization_spec(
                    box=[obj["x"], obj["y"], obj["xx"], obj["xy"]],
                    version_id=version_id,
                    label=info_data["best_label"][0],
                    width=video_width,
                    height=video_height,
                    attributes=attributes,
                    frame_number=info_data["best_frame"],
                    type_id=tdwa_box_type.id,
                    media_id=media_id,
                    project_id=tator_project.id,
                    normalize=False,
                ))

            # Load tdwa_box
            tdwa_box_ids = load_bulk_boxes(tator_project.id, api, tdwa_box_specs)
            info(f"Loaded {len(tdwa_box_ids)} tdwa_boxes into Tator")

            # Create states for non-merged tracks
            states = []
            for tracker_id in track_info:
                # Skip if this track was merged into another
                if tracker_id in merged_tracker_map:
                    continue
                
                info_data = track_info[tracker_id]
                attributes_best = {
                    "label": info_data["best_label"],
                    "max_score": info_data["score"],
                    "verified": True,
                    "num_frames": info_data["last_frame"] - info_data["first_frame"] + 1
                }
                attributes = format_attributes(attributes_best, track_attributes)
                if 'label' in attributes:
                    attributes["Label"] = attributes.pop("label")
                state = {
                    "type": track_type.id,
                    "media_ids": [media_id],
                    "localization_ids": localization_ids[tracker_id],
                    "attributes": attributes,
                    "version": version_id,
                    "frame": info_data["best_frame"],
                }
                states.append(state)

            # Load tracks
            state_ids = []
            for response in tator.util.chunked_create(
                    api.create_state_list, video_type.project, body=states
            ):
                state_ids += response.id
                num_loaded_tracks += len(response.id)
            info(f"Created {len(state_ids)} tracks!")

            info(f"Successfully loaded {num_loaded_boxes} localizations and {num_loaded_tracks} tracks into Tator")
            return num_loaded_tracks

    except Exception as e:
        err(f"Error: {e}")
        raise e


def soft_iou(box1: Tuple[float, float, float, float], 
             box2: Tuple[float, float, float, float],
             sigma: float = 0.5) -> float:
    """
    Compute soft IoU between two bounding boxes using Gaussian weighting.
    
    Args:
        box1: (x1, y1, x2, y2) - first bounding box
        box2: (x1, y1, x2, y2) - second bounding box
        sigma: Gaussian sigma for soft weighting (default 0.5)
    
    Returns:
        Soft IoU value between 0 and 1
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Calculate intersection
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)
    
    if x_right < x_left or y_bottom < y_top:
        intersection = 0.0
    else:
        intersection = (x_right - x_left) * (y_bottom - y_top)
    
    # Calculate areas
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    # Standard IoU
    iou = intersection / union
    
    # Calculate center distance for soft weighting
    center1 = np.array([(x1_1 + x2_1) / 2, (y1_1 + y2_1) / 2])
    center2 = np.array([(x1_2 + x2_2) / 2, (y1_2 + y2_2) / 2])
    center_dist = np.linalg.norm(center1 - center2)
    
    # Normalize distance by diagonal of union box
    x_min_union = min(x1_1, x1_2)
    y_min_union = min(y1_1, y1_2)
    x_max_union = max(x2_1, x2_2)
    y_max_union = max(y2_1, y2_2)
    diagonal = np.sqrt((x_max_union - x_min_union)**2 + (y_max_union - y_min_union)**2)
    
    if diagonal > 0:
        normalized_dist = center_dist / diagonal
    else:
        normalized_dist = 0
    
    # Apply Gaussian weighting to IoU based on center distance
    weight = np.exp(-(normalized_dist ** 2) / (2 * sigma ** 2))
    soft_iou_value = iou * weight
    
    return soft_iou_value


@dataclass
class Prediction:
    """Single prediction event."""
    label: str
    score: float
    frame_num: float   # seconds, or any monotonic value
    df_row_index: int # row index of the box in the dataframe


class TimeDecayWeightedAverage:
    """
    Computes a time-decayed weighted average of predictions.
    Also tracks the best individual prediction.
    """

    def __init__(self, half_life: float = 15.0):
        """
        half_life: time where weight = 0.8
        """
        self.half_life = half_life
        self.decay_const = math.log(2) / half_life

        self.predictions: List[Prediction] = []

    def add(self, label: str, score: float, frame_num: float, df_row_index: int):
        p = Prediction(label, score, frame_num, df_row_index)
        self.predictions.append(p)

    def _weight(self, t_now, t_pred):
        dt = t_pred - t_now  # negative for older
        return math.exp(self.decay_const * dt)

    def time_decay_average(self, current_frame_num: float) -> Tuple[str, float, float, int]:
        """
        Returns (label, weighted_score, frame_num, box_row_index) for the best prediction.
        where weighted_score is aggregated across all predictions.
        """
        if not self.predictions:
            return "", 0.0, current_frame_num, -1

        # Aggregate scores by label
        scores = {}
        weights = {}

        for p in self.predictions:
            w = self._weight(current_frame_num, p.frame_num)

            scores[p.label] = scores.get(p.label, 0.0) + p.score * w
            weights[p.label] = weights.get(p.label, 0.0) + w

        # Print the weights
        for label, weight in weights.items():
            print(f"{label}: {weight}")

        # Weighted average per label
        weighted_avgs = {
            label: scores[label] / weights[label]
            for label in scores
        }

        for label, score in weighted_avgs.items():
            print(f"{label}: weighted {score}")

        # Choose the label with the highest weighted avg
        best_label = max(weighted_avgs.items(), key=lambda x: x[1])

        # Get all labels with the best
        all_best_predictions = [p for p in self.predictions if p.label == best_label[0]]
        # Get the maximum score for the best label
        best_score = max([p.score for p in all_best_predictions])
        # Get the frame and box where the best score is achieved
        best_frame_num = [p.frame_num for p in all_best_predictions if p.score == best_score][0] 
        df_row_index = [p.df_row_index for p in all_best_predictions if p.frame_num == best_frame_num][0]
        # weighted_avg = best[1]
        return best_label, best_score, best_frame_num, df_row_index


if __name__ == "__main__":
    import os

    # To run this script, you need to have the TATOR_TOKEN environment variable set
    os.environ["ENVIRONMENT"] = "TESTING"
    test_path = Path(__file__).parent.parent.parent / "tests" / "data" / "i2map" / "i2MAP_20250403T092817Z_1000m_F031_25-tracks.tar.gz"
    yaml_path = Path(__file__).parent.parent.parent / "tests" / "config" / "config_i2map.yml"
    tator_token = os.getenv("TATOR_TOKEN")

    if test_path.exists():
        load_tracks(
            token=tator_token,
            config=yaml_path.as_posix(),
            dry_run=True,
            version="Baseline",
            input=test_path,
            max_num=10,
            disable_ssl_verify=False,
            iou_threshold=0.3,
            frame_gap=5
        )
    else:
        print(f"Test file {test_path} does not exist")

