# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/localization.py
# Description: Load localizations into the database

import tator  # type: ignore

from mbari_aidata.logger import info
from typing import List


def gen_spec(
    box: List[float],
    version_id: int,
    label: str,
    width: int,
    height: int,
    frame_number: int,
    type_id: int,
    media_id: int,
    project_id: int,
    attributes: dict,
    normalize: bool = True,
) -> dict:
    """
    Generate a media spec for Tator
    :param box: box data [x1, y1, x2, y2]
    :param version_id: Version ID to associate to the localization.
    :param label: label of the box
    :param width: width of the image
    :param height: height of the image
    :param frame_number: frame number in the video (if video) 0-indexed, or 0 if image
    :param media_id: media ID
    :param type_id: box type ID
    :param project_id: project ID
    :param attributes: additional attributes
    :param normalize: If True, normalize the box to 0-1
    :return: The localization spec
    """
    attributes["Label"] = label
    x1, y1, x2, y2 = box

    if normalize:
        x, y = x1 / width, y1 / height
        w, h = (x2 - x1) / width, (y2 - y1) / height
    else:
        x, y = x1, y1
        w, h = x2 - x1, y2 - y1

    # Clamp dimensions to valid range
    w = max(0.0, min(1.0, w))
    h = max(0.0, min(1.0, h))

    # Adjust if box extends beyond boundaries
    if x + w > 1.0:
        w = 1.0 - x
        info(f"Localization too large {x}+{w} {box}")
    if y + h > 1.0:
        h = 1.0 - y
        info(f"Localization too large {y}+{h} {box}")

    # Final position clamping
    x = max(0.0, min(1.0, x))
    y = max(0.0, min(1.0, y))

    spec = {
        "version": version_id,
        "type": type_id,
        "media_id": media_id,
        "project": project_id,
        "x": x,
        "y": y,
        "width": w,
        "height": h,
        "frame": frame_number,
        "attributes": attributes,
    }
    return spec


def load_bulk_boxes(project_id, api, specs):
    """
    Bulk load localization boxes associated with a media into the database
    :param api: Tator API
    :param project_id: project ID
    :param specs: List of localization specs
    :return:
    """
    info(f"Loading {len(specs)} localizations into Tator")
    chunk_size = min(200, len(specs))
    loc_ids = [
        new_id
        for response in tator.util.chunked_create(
            api.create_localization_list, project_id, chunk_size=chunk_size, body=specs
        )
        for new_id in response.id
    ]
    info(f"Loaded {len(loc_ids)} localizations into Tator")
    return loc_ids
