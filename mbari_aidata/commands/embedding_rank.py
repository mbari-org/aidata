# mbari_aidata, Apache-2.0 license
# Filename: commands/embedding_rank.py
# Description: Compute embeddings and similarity ranking for TDWA boxes
import tempfile
import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np
from PIL import Image
import torch

from mbari_aidata.logger import info, err, debug
from transformers import AutoModel, AutoImageProcessor  # type: ignore


def crop_boxes_from_video(
    video_path: str,
    boxes: List[Tuple[float, float, float, float]],
    frames: List[int],
    fps: float,
    video_width: int,
    video_height: int,
    resize: int = None
) -> List[Image.Image]:
    """
    Crop boxes from video frames using ffmpeg, similar to coco_voc.py implementation.

    Args:
        video_path: Path to the video file
        boxes: List of (x, y, xx, xy) normalized coordinates
        frames: List of frame numbers
        fps: Frames per second of the video
        video_width: Width of the video
        video_height: Height of the video
        resize: Optional resize dimension

    Returns:
        List of PIL Images cropped from the video
    """
    cropped_images = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, (box, frame) in enumerate(zip(boxes, frames)):
            x1, y1, x2, y2 = box

            # Convert normalized coordinates to pixel coordinates
            x1 = int(x1 * video_width)
            y1 = int(y1 * video_height)
            x2 = int(x2 * video_width)
            y2 = int(y2 * video_height)

            # Ensure coordinates are within bounds
            x1, x2 = max(0, x1), min(video_width, x2)
            y1, y2 = max(0, y1), min(video_height, y2)

            # Calculate width and height
            width = x2 - x1
            height = y2 - y1

            # Make square by padding the shorter side
            if width > height:
                padding = (width - height) // 2
                y1 = max(0, y1 - padding)
                y2 = min(video_height, y2 + padding)
            else:
                padding = (height - width) // 2
                x1 = max(0, x1 - padding)
                x2 = min(video_width, x2 + padding)

            # Convert frame number to timestamp
            total_seconds = frame / fps
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

            # Output path for cropped image
            output_path = Path(tmpdir) / f"crop_{i}.jpg"

            # Build ffmpeg command
            filter_str = f"crop={x2-x1}:{y2-y1}:{x1}:{y1}"
            if resize:
                filter_str += f",scale={resize}:{resize}"

            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output files
                "-loglevel", "panic",  # Suppress logs
                "-nostats",
                "-hide_banner",
                "-ss", timestamp,  # Seek to timestamp
                "-i", video_path,  # Input video
                "-vf", filter_str,  # Video filter
                "-frames:v", "1",  # Extract one frame
                "-q:v", "2",  # High quality
                str(output_path)
            ]

            try:
                result = subprocess.run(cmd, check=True, capture_output=True)
                if output_path.exists():
                    # Load the cropped image
                    img = Image.open(output_path).convert("RGB")
                    cropped_images.append(img)
                else:
                    err(f"Failed to create cropped image for frame {frame}")
                    cropped_images.append(None)
            except subprocess.CalledProcessError as e:
                err(f"ffmpeg failed for frame {frame}: {e}")
                cropped_images.append(None)

    return cropped_images


def compute_embeddings_for_boxes(
    cropped_images: List[Image.Image],
    model_info: Dict[str, Any]
) -> np.ndarray:
    """
    Compute embeddings for a list of cropped images using ViT.

    Args:
        cropped_images: List of PIL Images
        model_info: Dictionary with 'processor', 'model', and 'device'

    Returns:
        Numpy array of embeddings
    """
    # Filter out None images (failed crops)
    valid_images = [img for img in cropped_images if img is not None]

    if not valid_images:
        return np.array([])

    # Preprocess images
    processor = model_info["processor"]
    model = model_info["model"]
    device = model_info["device"]
    
    inputs = processor(images=valid_images, return_tensors="pt").to(device)

    # Get embeddings
    with torch.no_grad():
        embeddings = model(**inputs)
    batch_embeddings = embeddings.last_hidden_state[:, 0, :].cpu().numpy()
    
    return np.array(batch_embeddings)


def compute_similarity_ranking(
    query_embedding: np.ndarray,
    candidate_embeddings: np.ndarray,
    candidate_ids: List[Any]
) -> List[Tuple[Any, float]]:
    """
    Compute cosine similarity ranking between query and candidates.

    Args:
        query_embedding: Single embedding vector
        candidate_embeddings: Array of candidate embeddings
        candidate_ids: IDs corresponding to candidate embeddings

    Returns:
        List of (id, similarity_score) tuples sorted by similarity (descending)
    """
    if len(candidate_embeddings) == 0:
        return []

    # Compute cosine similarity
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    candidate_norms = candidate_embeddings / np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)

    similarities = np.dot(candidate_norms, query_norm)

    # Create ranking list
    ranking = list(zip(candidate_ids, similarities.astype(float)))
    ranking.sort(key=lambda x: x[1], reverse=True)

    return ranking


def rank_tdwa_boxes_by_similarity(
    tdwa_boxes: List[Dict[str, Any]],
    video_path: str,
    fps: float,
    video_width: int,
    video_height: int,
    config_dict: Dict[str, Any],
    device: str = "cpu",
    resize: int = None
) -> Dict[str, List[Tuple[Any, float]]]:
    """
    Main function to rank TDWA boxes by embedding similarity.

    Args:
        tdwa_boxes: List of TDWA box dictionaries with keys like 'x', 'y', 'xx', 'xy', 'frame', 'id'
        video_path: Path to the video file
        fps: Frames per second
        video_width: Video width in pixels
        video_height: Video height in pixels
        config_dict: Configuration dictionary containing vss.model
        device: Device for model inference ('cpu' or 'cuda:X')
        resize: Optional resize dimension for cropped images

    Returns:
        Dictionary mapping box IDs to similarity rankings
    """
    info(f"Starting embedding ranking for {len(tdwa_boxes)} TDWA boxes")

    if not tdwa_boxes:
        return {}

    # Extract box coordinates and frames
    boxes = []
    frames = []
    box_ids = []

    for box in tdwa_boxes:
        boxes.append((box['x'], box['y'], box['xx'], box['xy']))
        frames.append(box['frame'])
        box_ids.append(box['id'])

    # Crop boxes from video
    info(f"Cropping {len(boxes)} boxes from video {video_path}")
    cropped_images = crop_boxes_from_video(
        video_path, boxes, frames, fps, video_width, video_height, resize
    )

    successful_crops = sum(1 for img in cropped_images if img is not None)
    info(f"Successfully cropped {successful_crops}/{len(cropped_images)} boxes")

    if successful_crops == 0:
        err("No boxes were successfully cropped")
        return {}

    # Initialize ViT model
    try:
        model_name = config_dict["vss"]["model"]
        
        info(f"Loading model {model_name}")
        processor = AutoImageProcessor.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Move model to device
        if 'cuda' in device and torch.cuda.is_available():
            device_num = int(device.split(":")[-1])
            info(f"Using GPU device {device_num}")
            torch.cuda.set_device(device_num)
            model.to("cuda")
            device_str = "cuda"
        else:
            device_str = "cpu"
        
        model_info = {"processor": processor, "model": model, "device": device_str}
    except KeyError as e:
        err(f"Missing required configuration key: {e}")
        return {}
    except Exception as e:
        err(f"Failed to initialize model: {e}")
        return {}

    # Compute embeddings for all cropped boxes
    info("Computing embeddings for cropped boxes")
    embeddings = compute_embeddings_for_boxes(cropped_images, model_info)

    if len(embeddings) == 0:
        err("No embeddings were computed")
        return {}

    # For each box, compute similarity ranking against all other boxes
    rankings = {}

    # Filter out failed crops and their corresponding data
    valid_indices = [i for i, img in enumerate(cropped_images) if img is not None]
    valid_embeddings = embeddings
    valid_box_ids = [box_ids[i] for i in valid_indices]

    info(f"Computing similarity rankings for {len(valid_embeddings)} valid embeddings")

    for i, (query_emb, query_id) in enumerate(zip(valid_embeddings, valid_box_ids)):
        # Remove the query embedding from candidates
        candidate_embeddings = np.delete(valid_embeddings, i, axis=0)
        candidate_ids = [bid for j, bid in enumerate(valid_box_ids) if j != i]

        # Compute ranking
        ranking = compute_similarity_ranking(query_emb, candidate_embeddings, candidate_ids)
        rankings[query_id] = ranking

        if (i + 1) % 10 == 0:
            info(f"Processed ranking for {i + 1}/{len(valid_embeddings)} boxes")

    info(f"Completed similarity ranking for {len(rankings)} TDWA boxes")
    return rankings

