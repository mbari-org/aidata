# mbari_aidata, Apache-2.0 license
# Filename: generators/localization_csv.py
# Description: Helper functions for generating a localizations CSV from Tator data
from typing import Any, Iterable, List


def get_localization_attribute_columns(all_localizations: Iterable[Any]) -> List[str]:
    """
    Collect the sorted union of all attribute keys across every localization.
    Analogous to get_media_attribute_columns for media objects.
    """
    columns: set = set()
    for loc in all_localizations:
        attributes = getattr(loc, "attributes", None)
        if attributes and hasattr(attributes, "keys"):
            columns.update(attributes.keys())
    return sorted(columns)


def get_media_attribute_columns(all_media: Iterable[Any]) -> List[str]:
    """
    Collect the sorted union of all attribute keys across every media item.
    """
    columns: set = set()
    for media in all_media:
        attributes = getattr(media, "attributes", None)
        if attributes and hasattr(attributes, "keys"):
            columns.update(attributes.keys())
    return sorted(columns)


def get_localization_csv_row(
    media: Any,
    localization: Any,
    localization_attribute_columns: List[str],
    media_attribute_columns: List[str],
) -> List[Any]:
    """
    Build a CSV row for a single localization.

    Column order: media, frame, uuid, <localization attributes...>, x, y, width, height,
    <media attributes...>
    """
    loc_attrs = getattr(localization, "attributes", None) or {}
    media_attrs = getattr(media, "attributes", None) or {}

    row: List[Any] = [media.name, localization.frame, localization.elemental_id]

    for col in localization_attribute_columns:
        row.append(loc_attrs.get(col, ""))

    row.extend([localization.x, localization.y, localization.width, localization.height])

    for col in media_attribute_columns:
        row.append(media_attrs.get(col, ""))

    return row
