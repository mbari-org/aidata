# mbari_aidata, Apache-2.0 license
# Filename: tests/test_coco_voc_localizations_csv.py
# Description: Tests for dynamic localization and media attribute column discovery and CSV row building
from types import SimpleNamespace

from mbari_aidata.generators.localization_csv import (
    get_localization_attribute_columns,
    get_media_attribute_columns,
    get_localization_csv_row,
)


def _make_loc(attributes, x=0.1, y=0.2, width=0.3, height=0.4, frame=5, elemental_id="abc-123", media_id=1):
    return SimpleNamespace(
        attributes=attributes,
        x=x,
        y=y,
        width=width,
        height=height,
        frame=frame,
        elemental_id=elemental_id,
        media=media_id,
    )


def _make_media(attributes, name="image.jpg", media_id=1):
    return SimpleNamespace(attributes=attributes, name=name, id=media_id)


# ---------------------------------------------------------------------------
# get_localization_attribute_columns
# ---------------------------------------------------------------------------

def test_get_localization_attribute_columns_returns_sorted_union():
    locs = [
        _make_loc({"Label": "fish", "score": 0.9, "verified": True}),
        _make_loc({"Label": "shrimp", "cluster": "A", "saliency": 500}),
    ]
    cols = get_localization_attribute_columns(locs)
    assert cols == sorted({"Label", "score", "verified", "cluster", "saliency"})


def test_get_localization_attribute_columns_empty_list():
    assert get_localization_attribute_columns([]) == []


def test_get_localization_attribute_columns_none_attributes():
    loc = _make_loc(None)
    assert get_localization_attribute_columns([loc]) == []


def test_get_localization_attribute_columns_single_loc():
    locs = [_make_loc({"custom_field": "value", "Label": "eel"})]
    cols = get_localization_attribute_columns(locs)
    assert cols == ["Label", "custom_field"]


def test_get_localization_attribute_columns_deduplicates():
    locs = [
        _make_loc({"Label": "fish", "score": 0.8}),
        _make_loc({"Label": "crab", "score": 0.5}),
    ]
    cols = get_localization_attribute_columns(locs)
    assert cols.count("Label") == 1
    assert cols.count("score") == 1


# ---------------------------------------------------------------------------
# get_media_attribute_columns
# ---------------------------------------------------------------------------

def test_get_media_attribute_columns_collects_sorted_unique_keys():
    media = [
        SimpleNamespace(attributes={"iso_datetime": "2024-01-01T00:00:00Z", "depth": 100}),
        SimpleNamespace(attributes={"depth": 200, "section": "A"}),
        SimpleNamespace(attributes=None),
    ]
    columns = get_media_attribute_columns(media)
    assert columns == ["depth", "iso_datetime", "section"]


def test_get_media_attribute_columns_returns_sorted_union():
    media = [
        _make_media({"depth": 100, "section": "transect-1"}),
        _make_media({"depth": 200, "temperature": 4.5}),
    ]
    cols = get_media_attribute_columns(media)
    assert cols == sorted({"depth", "section", "temperature"})


def test_get_media_attribute_columns_empty_list():
    assert get_media_attribute_columns([]) == []


def test_get_media_attribute_columns_none_attributes():
    m = _make_media(None)
    assert get_media_attribute_columns([m]) == []


# ---------------------------------------------------------------------------
# get_localization_csv_row
# ---------------------------------------------------------------------------

def test_get_localization_csv_row_basic():
    loc = _make_loc({"Label": "fish", "score": 0.9}, x=0.1, y=0.2, width=0.3, height=0.4, frame=7, elemental_id="uuid-1")
    media = _make_media({"depth": 150}, name="frame007.jpg")

    loc_cols = ["Label", "score"]
    media_cols = ["depth"]

    row = get_localization_csv_row(media, loc, loc_cols, media_cols)
    assert row == ["frame007.jpg", 7, "uuid-1", "fish", 0.9, 0.1, 0.2, 0.3, 0.4, 150]


def test_get_localization_csv_row_missing_attribute_uses_empty_string():
    loc = _make_loc({"Label": "eel"}, frame=0, elemental_id="uuid-2")
    media = _make_media({}, name="img.jpg")

    loc_cols = ["Label", "cluster", "saliency"]
    media_cols = ["depth", "section"]

    row = get_localization_csv_row(media, loc, loc_cols, media_cols)
    assert row[4] == ""  # cluster absent
    assert row[5] == ""  # saliency absent
    assert row[10] == ""  # depth absent
    assert row[11] == ""  # section absent


def test_get_localization_csv_row_column_order():
    loc = _make_loc({"Label": "fish", "score": 0.5}, x=0.0, y=0.1, width=0.2, height=0.3, frame=1, elemental_id="eid")
    media = _make_media({"section": "s1"}, name="m.jpg")

    loc_cols = ["Label", "score"]
    media_cols = ["section"]

    row = get_localization_csv_row(media, loc, loc_cols, media_cols)
    # [media.name, frame, uuid, Label, score, x, y, w, h, section]
    assert row == ["m.jpg", 1, "eid", "fish", 0.5, 0.0, 0.1, 0.2, 0.3, "s1"]


def test_get_localization_csv_row_no_columns():
    loc = _make_loc({}, frame=3, elemental_id="e3", x=0.5, y=0.5, width=0.1, height=0.1)
    media = _make_media({}, name="bare.jpg")

    row = get_localization_csv_row(media, loc, [], [])
    assert row == ["bare.jpg", 3, "e3", 0.5, 0.5, 0.1, 0.1]
