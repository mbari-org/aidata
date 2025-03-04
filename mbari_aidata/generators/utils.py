# mbari_aidata, Apache-2.0 license
# Filename: generators/utils.py
# Description: Algorithms to run on lists of localizations to combine them and crop frames
from typing import List
from tator.openapi.tator_openapi import Localization  # type: ignore
import pandas as pd
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

def combine_localizations(boxes: List[Localization]) -> List[Localization]:
    """
    Combine localizations using a voting algorithm on a list of localizations
    :param boxes: List of Localization objects with x, y, width, height, label, and score attributes
    :return: List of Localization objects
    """
    # First, convert the list of localizations to a DataFrame
    labels = [box.attributes["Label"] for box in boxes]
    score = [box.attributes["score"] for box in boxes]
    x = [box.x for box in boxes]
    y = [box.y for box in boxes]
    width = [box.width for box in boxes]
    height = [box.height for box in boxes]
    df = pd.DataFrame({"x": x, "y": y, "width": width, "height": height, "label": labels, "score": score})

    # Assign unique x, y, width, height a unique identifier - this will be used to group the localizations
    df["id"] = df.groupby(["x", "y", "width", "height"]).ngroup()

    # Group by 'id', count occurrences, and find the label with the maximum count
    # Note that in the case of a tie, the first label will be chosen
    max_labels = df.groupby("id")["label"].apply(lambda x: x.value_counts().idxmax()).reset_index(name="max_label")

    # Merge the maximum labels with the original data
    max_labels = max_labels.merge(df, on="id", how="left")

    # Drop any duplicate rows - we only want one row per 'id'
    max_labels.drop_duplicates(subset=["id"], inplace=True)

    # Create a new list of Localization objects with the winners
    max_boxes = []
    for index, row in max_labels.iterrows():
        max_boxes.append(
            Localization(
                x=row["x"],
                y=row["y"],
                width=row["width"],
                height=row["height"],
                attributes={"Label": row["label"], "score": row["score"]},
            )
        )

    return max_boxes


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
