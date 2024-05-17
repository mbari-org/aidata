# aidata, Apache-2.0 license
# Filename: generators/utils.py
# Description: Algorithms to run on lists of localizations to combine them
from typing import List
from tator.openapi.tator_openapi import Localization
import pandas as pd

from aidata.logger import debug


def combine_localizations(boxes: List[Localization]) -> List[Localization]:
    """
    Combine localizations using a voting algorithm on a list of localizations
    :param boxes: List of Localization objects
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

    debug(max_labels)

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
