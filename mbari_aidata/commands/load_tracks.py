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
import tator  # type: ignore


@click.command("tracks", help="Load tracks from a .tar.gz file with track data")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.dry_run
@common_args.version
@click.option("--input", type=Path, required=True, help=".tar.gz file containing track data")
@click.option("--max-num", type=int, help="Maximum number of localizations in tracks to load")
def load_tracks(token: str, disable_ssl_verify: bool, config: str, version: str, input: Path, dry_run: bool, max_num: int) -> int:
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
        video_type = find_media_type(api, tator_project.id, "Video")

        assert "box" in config_dict["tator"], "Missing required 'box' key in configuration file"
        assert "track_state" in config_dict["tator"], "Missing required 'track_state' key in configuration file"

        box_attributes = config_dict["tator"]["box"]["attributes"]
        track_attributes = config_dict["tator"]["track_state"]["attributes"]

        assert version_id is not None, f"No version found in project {project}"
        assert box_type is not None, f"No box type found in project {project} for type Box"
        assert track_type is not None, f"No state type found in project {project} for type Track"
        assert video_type is not None, f"No track type found in project {project} for type Video"

        info(f"Processing track data from {input}")

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
            video_name = video_name.replace('.mov', '.mp4') #only support .mp4 videos for now
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

            # Load tracks
            states = []
            for i, row in df_tracks.iterrows():
                obj = row.to_dict()
                tracker_id = obj["tracker_id"]
                if tracker_id not in localization_ids:
                    warn(f"No localizations found for track {tracker_id}")
                    continue
                if len(localization_ids[tracker_id]) == 0:
                    warn(f"No localizations found for track {tracker_id}")
                    continue
                info(f"Row {i} Track {tracker_id}: frames {obj['first_frame']} to {obj['last_frame']}")
                attributes = format_attributes(obj, track_attributes)
                first_frame = obj["first_frame"]
                last_frame = obj["last_frame"]
                middle_frame = (first_frame + last_frame) // 2
                state = {
                    "type": track_type.id,
                    "media_ids": [media_id],
                    "localization_ids": localization_ids[tracker_id],
                    "attributes": attributes,
                    "version": version_id,
                    "frame": middle_frame,
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


    except Exception as e:
        err(f"Error: {e}")
        raise e


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
            disable_ssl_verify=False
        )
    else:
        print(f"Test file {test_path} does not exist")

