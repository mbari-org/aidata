# mbari_aidata, Apache-2.0 license
# Filename: generators/utils.py
# Description: Algorithms to run on lists of localizations to combine them and crop frames
from typing import List, Optional
from tator.openapi.tator_openapi import Localization  # type: ignore
import torch
from torchvision.ops import nms
import xml.etree.ElementTree as ET
import subprocess
import os
import shlex

from mbari_aidata.logger import err, debug


def build_roi_crop_filter(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    media_width: int,
    media_height: int,
    resize: int = 0,
    fill: Optional[str] = None,
) -> str:
    """
    Build an ffmpeg video filter to crop a localization ROI to a square.

    When ``fill`` is ``black`` or ``white``, out-of-bounds padding needed to
    square the crop is filled with that color instead of clipping the ROI.
    """
    width = x2 - x1
    height = y2 - y1
    if width <= 0 or height <= 0:
        return ""
    shorter_side = min(height, width)
    longer_side = max(height, width)
    padding = abs(longer_side - shorter_side) // 2

    sq_x1, sq_y1, sq_x2, sq_y2 = x1, y1, x2, y2
    if width == shorter_side:
        sq_x1 -= padding
        sq_x2 += padding
    else:
        sq_y1 -= padding
        sq_y2 += padding

    crop_x1 = max(0, sq_x1)
    crop_y1 = max(0, sq_y1)
    crop_x2 = min(media_width, sq_x2)
    crop_y2 = min(media_height, sq_y2)
    crop_w = crop_x2 - crop_x1
    crop_h = crop_y2 - crop_y1
    if crop_w <= 0 or crop_h <= 0:
        return ""

    if fill:
        ideal_w = sq_x2 - sq_x1
        ideal_h = sq_y2 - sq_y1
        ideal_size = max(ideal_w, ideal_h, crop_w, crop_h)
        if ideal_size <= 0:
            return ""

        pad_x = crop_x1 - sq_x1
        pad_y = crop_y1 - sq_y1
        if pad_x < 0 or pad_y < 0:
            return ""

        required_w = crop_w + pad_x
        required_h = crop_h + pad_y
        ideal_size = max(ideal_size, required_w, required_h)
        crop_filter = (
            f"crop={crop_w}:{crop_h}:{crop_x1}:{crop_y1},"
            f"pad={ideal_size}:{ideal_size}:{pad_x}:{pad_y}:{fill}"
        )
    else:
        crop_filter = f"crop={crop_w}:{crop_h}:{crop_x1}:{crop_y1}"

    if resize:
        return f"{crop_filter},scale={resize}:{resize}"
    return crop_filter


FFMPEG_TIMEOUT_SECS = 10  # seconds before an ffmpeg crop is considered hung


def crop_frame(args):
    """Helper function to run the ffmpeg command for a single crop"""
    crop, out, inputs = args
    if os.path.exists(out):
        return 1  # Skip if the output file already exists
    cmd = ["ffmpeg"] + inputs + ["-vf", crop, "-frames:v", "1", out]
    debug(shlex.join(cmd))
    try:
        subprocess.run(
            cmd,
            check=True,
            shell=False,
            capture_output=True,
            text=True
        )
        return 1
    except subprocess.TimeoutExpired as e:
        err(f"ffmpeg timed out after {FFMPEG_TIMEOUT_SECS}s for output {out}: {e}")
        return 0
    except subprocess.CalledProcessError as e:
        err(str(e))
        if e.stderr:
            err(f"ffmpeg stderr: {e.stderr.strip()}")
        if e.stdout:
            debug(f"ffmpeg stdout: {e.stdout.strip()}")
        return 0


def crop_frame_multi(args):
    """
    Run a single ffmpeg invocation to extract all ROI crops from one (source, frame) pair.

    Uses ``-filter_complex split`` with N outputs so the video is only decoded and
    seeked once regardless of how many localizations share that frame.

    args: (base_inputs, [(filter_str, out_path), ...])
      base_inputs — ffmpeg args up to and including ``-i <source>`` (no ``-vf``)
      pairs       — one (filter_str, out_path) per ROI in this frame
    """
    base_inputs, pairs = args
    pairs = [(c, o) for c, o in pairs if not os.path.exists(o)]
    if not pairs:
        return 0

    n = len(pairs)
    if n == 1:
        crop, out = pairs[0]
        cmd = ["ffmpeg"] + list(base_inputs) + ["-vf", crop, "-frames:v", "1", out]
        debug(shlex.join(cmd))
        try:
            subprocess.run(cmd, check=True, shell=False, capture_output=True, text=True)
            return 1
        except subprocess.TimeoutExpired as e:
            err(f"ffmpeg timed out for {out}: {e}")
            return 0
        except subprocess.CalledProcessError as e:
            err(str(e))
            if e.stderr:
                err(f"ffmpeg stderr: {e.stderr.strip()}")
            return 0

    # Build filter_complex: split the single decoded frame into N streams, one crop per stream
    split_labels = [f"s{i}" for i in range(n)]
    out_labels = [f"o{i}" for i in range(n)]
    filter_parts = [f"[0:v]split={n}{''.join(f'[{s}]' for s in split_labels)}"]
    for i, (crop_filter, _) in enumerate(pairs):
        filter_parts.append(f"[{split_labels[i]}]{crop_filter}[{out_labels[i]}]")
    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg"] + list(base_inputs) + ["-filter_complex", filter_complex]
    for i, (_, out) in enumerate(pairs):
        cmd += ["-map", f"[{out_labels[i]}]", "-frames:v", "1", out]

    debug(shlex.join(cmd))
    try:
        subprocess.run(cmd, check=True, shell=False, capture_output=True, text=True)
        return n
    except subprocess.TimeoutExpired as e:
        err(f"ffmpeg timed out for frame group ({n} crops): {e}")
        return 0
    except subprocess.CalledProcessError as e:
        err(str(e))
        if e.stderr:
            err(f"ffmpeg stderr: {e.stderr.strip()}")
        return 0

def combine_localizations(boxes: List[Localization], iou_threshold: float = 0.5) -> List[Localization]:
    """
    Combine localizations using torch/torchvision NMS (per class).
    Keeps highest-score boxes and suppresses overlaps >= IoU threshold.

    :param boxes: List of Localization objects with x, y, width, height, label, and score attributes
    :param iou_threshold: IoU threshold for suppressing overlapping boxes (default: 0.5)
    :return: List of Localization objects
    """
    if not boxes:
        return []

    # Group indices by label for class-wise NMS
    label_to_indices = {}
    for idx, box in enumerate(boxes):
        label = box.attributes.get("Label", "Unknown")
        if label not in label_to_indices:
            label_to_indices[label] = []
        label_to_indices[label].append(idx)

    idxs = range(len(boxes))

    xyxy = torch.tensor([ [ b.x, b.y, b.x + b.width, b.y + b.height ] for b in boxes], dtype=torch.float32)
    scores = torch.tensor([ float(b.attributes.get("score", 0.0)) for b in boxes ], dtype=torch.float32)

    keep_rel = nms(xyxy, scores, iou_threshold)
    kept_indices = [idxs[i] for i in keep_rel.tolist()]

    # Reconstruct Localization objects for kept boxes
    result: List[Localization] = [boxes[i] for i in kept_indices]
    return result


def parse_voc_xml(xml_file) -> List:
    """
    Parse a VOC XML file and return the bounding boxes, labels, poses, and ids
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    boxes = []
    labels = []
    poses = []
    ids = []

    image_size = root.find('size')
    image_width = int(image_size.find('width').text)
    image_height = int(image_size.find('height').text)

    for obj in root.findall('object'):
        label = obj.find('name').text
        pose = obj.find('pose').text if obj.find('pose') is not None else "Unspecified"
        id = obj.find('id').text if obj.find('id') is not None else ""
        bbox = obj.find('bndbox')
        xmin = int(bbox.find('xmin').text)
        ymin = int(bbox.find('ymin').text)
        xmax = int(bbox.find('xmax').text)
        ymax = int(bbox.find('ymax').text)

        # Make sure to bound the coordinates are within the image
        if xmin < 0:
            xmin = 0
        if ymin < 0:
            ymin = 0
        if xmax < 0:
            xmax = 0
        if ymax < 0:
            ymax = 0
        if xmax > image_width:
            xmax = image_width
        if ymax > image_height:
            ymax = image_height

        boxes.append([xmin, ymin, xmax, ymax])
        labels.append(label)
        poses.append(pose)
        ids.append(id)

    return boxes, labels, poses, ids
