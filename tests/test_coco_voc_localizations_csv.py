# mbari_aidata, Apache-2.0 license
# Filename: test_coco_voc_localizations_csv.py
# Description: Tests media attribute export helpers for localization CSV output
from types import SimpleNamespace

from mbari_aidata.generators.localization_csv import get_localization_csv_row, get_media_attribute_columns


def test_get_media_attribute_columns_collects_sorted_unique_keys():
    media = [
        SimpleNamespace(attributes={"iso_datetime": "2024-01-01T00:00:00Z", "depth": 100}),
        SimpleNamespace(attributes={"depth": 200, "section": "A"}),
        SimpleNamespace(attributes=None),
    ]

    columns = get_media_attribute_columns(media)

    assert columns == ["depth", "iso_datetime", "section"]


def test_get_localization_csv_row_appends_media_attributes():
    media = SimpleNamespace(name="media-1.mp4", attributes={"iso_datetime": "2024-01-01T00:00:00Z", "depth": 4123})
    localization = SimpleNamespace(
        frame=17,
        elemental_id="uuid-1",
        attributes={
            "verified": True,
            "cluster": "c1",
            "saliency": 0.9,
            "area": 10,
            "predicted_label": "pred",
            "Label": "gt",
            "score": 0.99,
            "label_s": "pred2",
            "score_s": 0.5,
        },
        x=0.1,
        y=0.2,
        width=0.3,
        height=0.4,
    )

    row = get_localization_csv_row(media, localization, ["depth", "iso_datetime", "section"])

    assert row == [
        "media-1.mp4", 17, "uuid-1", True, "c1", 0.9, 10, "pred", "gt", 0.99, "pred2", 0.5, 0.1, 0.2, 0.3, 0.4, 4123,
        "2024-01-01T00:00:00Z", "",
    ]
