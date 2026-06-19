# mbari_aidata, Apache-2.0 license
# Filename: generators/localization_csv.py
# Description: Helper functions for creating localization CSV rows with media attributes
from typing import Any, Iterable, List


def get_media_attribute_columns(all_media: Iterable[Any]) -> List[str]:
    columns = set()
    for media in all_media:
        attributes = getattr(media, "attributes", None)
        if isinstance(attributes, dict):
            columns.update(attributes.keys())
    return sorted(columns)


def get_localization_csv_row(media: Any, localization: Any, media_attribute_columns: List[str]) -> List[Any]:
    media_attributes = getattr(media, "attributes", None)
    if not isinstance(media_attributes, dict):
        media_attributes = {}

    localization_attributes = getattr(localization, "attributes", None)
    if not isinstance(localization_attributes, dict):
        localization_attributes = {}

    return [
        media.name,
        localization.frame,
        localization.elemental_id,
        localization_attributes.get("verified", False),
        localization_attributes.get("cluster", "Unknown"),
        localization_attributes.get("saliency", -1),
        localization_attributes.get("area", -1),
        localization_attributes.get("predicted_label", "Unknown"),
        localization_attributes.get("Label", "Unknown"),
        localization_attributes.get("score", 0),
        localization_attributes.get("label_s", "Unknown"),
        localization_attributes.get("score_s", 0),
        localization.x,
        localization.y,
        localization.width,
        localization.height,
        *[media_attributes.get(column, "") for column in media_attribute_columns],
    ]
