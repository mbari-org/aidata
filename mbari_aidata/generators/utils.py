# mbari_aidata, Apache-2.0 license
# Filename: generators/utils.py
# Description: Algorithms to run on lists of localizations to combine them and crop frames
from typing import List
from tator.openapi.tator_openapi import Localization  # type: ignore
import torch
from torchvision.ops import nms
import xml.etree.ElementTree as ET
import subprocess
import os

from mbari_aidata.logger import err, debug


def crop_frame(args):
    """Helper function to run the ffmpeg command for a single crop"""
    crop, out, inputs = args
    if os.path.exists(out):
        return 1  # Skip if the output file already exists
    args = ["ffmpeg"]
    args.extend(inputs)
    args.append(crop)
    args.append(out)
    debug(' '.join(args))
    try:
        subprocess.run(' '.join(args), check=False, shell=True)
        return 1
    except subprocess.CalledProcessError as e:
        err(str(e))
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

    kept_indices: List[int] = []

    for label, idxs in label_to_indices.items():
        # Build xyxy tensor and scores tensor
        xyxy = torch.tensor([
            [
                boxes[i].x,
                boxes[i].y,
                boxes[i].x + boxes[i].width,
                boxes[i].y + boxes[i].height,
            ]
            for i in idxs
        ], dtype=torch.float32)

        scores = torch.tensor([
            float(boxes[i].attributes.get("score", 0.0))
            for i in idxs
        ], dtype=torch.float32)

        if xyxy.numel() == 0:
            continue

        keep_rel = nms(xyxy, scores, iou_threshold)
        kept_indices.extend([idxs[i] for i in keep_rel.tolist()])

    # Reconstruct Localization objects for kept boxes
    result: List[Localization] = []
    for i in kept_indices:
        b = boxes[i]
        attrs = dict(b.attributes)
        if "score" not in attrs:
            attrs["score"] = float(attrs.get("score", 0.0))
        result.append(
            Localization(
                x=b.x,
                y=b.y,
                width=b.width,
                height=b.height,
                attributes=attrs,
            )
        )

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
