# mbari_aidata, Apache-2.0 license
# Filename: tests/test_sinker_planktivore_csv.py
# Description: Tests for the SINKER Planktivore mosaic CSV extractor
import csv
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image

from mbari_aidata.plugins.extractors.media_types import MediaType
from mbari_aidata.plugins.extractors.tap_sinker_planktivore_csv import (
    extract_media,
    extract_sinker_planktivore_csv,
    is_sinker_planktivore_csv,
    mosaic_path_from_roi_path,
    parse_roi_filename,
)
from mbari_aidata.plugins.loaders.tator.localization import gen_spec

STEM = "SINKER_20260827T221448.157843Z_PlanktivoreHM_40278598"
ROI_NAME = f"{STEM}_2411_192_67_55_0005.png"
ROI_PATH = (
    f"/mnt/Durkin_Data/SINKER_processed/PlanktivoreHM_40278598/2026/08/27/22/"
    f"extracted_rois/{STEM}/{ROI_NAME}"
)
UUID = "70c3697c-fc59-4f75-9112-464700cc607b"


def _write_csv(path: Path, rows) -> None:
    fieldnames = [
        "uuid",
        "path",
        "timestamp",
        "esd",
        "area",
        "w",
        "h",
        "track_id",
        "track_size",
        "is_duplicate",
        "is_kept",
        "focus_score",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _sample_row(path: str = ROI_PATH, uuid: str = UUID) -> dict:
    return {
        "uuid": uuid,
        "path": path,
        "timestamp": "2026-08-27T22:14:48.157843",
        "esd": 40.66863863729614,
        "area": 1299,
        "w": 55,
        "h": 67,
        "track_id": "55622a14-4f5b-48b8-8fb8-d01448c9eec5",
        "track_size": 2,
        "is_duplicate": True,
        "is_kept": False,
        "focus_score": 65.55532870597236,
    }


def test_parse_roi_filename():
    parsed = parse_roi_filename(ROI_NAME)
    assert parsed == {"stem": STEM, "x": 2411, "y": 192, "w": 67, "h": 55, "roi_idx": 5}


def test_mosaic_path_from_roi_path():
    media_path = mosaic_path_from_roi_path(Path(ROI_PATH), STEM)
    assert media_path == Path(
        f"/mnt/SINKER/MARS/PlanktivoreHM_40278598/2026/08/27/22/{STEM}.jpeg"
    )


def test_is_sinker_planktivore_csv(tmp_path):
    csv_path = tmp_path / "rois.csv"
    _write_csv(csv_path, [_sample_row()])
    assert is_sinker_planktivore_csv(csv_path)

    other = tmp_path / "sdcat.csv"
    other.write_text("image_path,x,y,xx,xy\n/tmp/a.jpg,0,0,1,1\n")
    assert not is_sinker_planktivore_csv(other)


def test_extract_boxes_normalizes_using_mosaic_size(tmp_path):
    mars_base = tmp_path / "MARS"
    mosaic = mars_base / "PlanktivoreHM_40278598/2026/08/27/22" / f"{STEM}.jpeg"
    mosaic.parent.mkdir(parents=True)
    Image.new("RGB", (4000, 3000), color="black").save(mosaic, "JPEG")

    csv_path = tmp_path / "rois.csv"
    _write_csv(csv_path, [_sample_row()])

    df = extract_sinker_planktivore_csv(csv_path, mars_base=mars_base)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["image_path"] == mosaic.as_posix()
    assert row["media_path"] == mosaic.as_posix()
    assert row["elemental_id"] == UUID
    assert row["image_width"] == 4000
    assert row["image_height"] == 3000
    assert row["x"] == 2411 / 4000
    assert row["y"] == 192 / 3000
    assert row["xx"] == (2411 + 67) / 4000
    assert row["xy"] == (192 + 55) / 3000
    assert row["label"] == "Unknown"
    assert row["score"] == 1.0
    assert row["w"] == 55
    assert row["h"] == 67


def test_extract_media_deduplicates_mosaics(tmp_path):
    csv_path = tmp_path / "rois.csv"
    second = ROI_PATH.replace("_0005.png", "_0006.png").replace("_2411_", "_1000_")
    _write_csv(csv_path, [_sample_row(), _sample_row(path=second, uuid="11111111-1111-1111-1111-111111111111")])

    df = extract_media(csv_path, mars_base=tmp_path / "MARS")
    assert len(df) == 1
    assert df.iloc[0]["media_type"] == MediaType.IMAGE
    assert STEM in df.iloc[0]["media_path"]
    assert not pd.isna(df.iloc[0]["iso_datetime"])


def test_extract_skips_unparseable_roi_name(tmp_path):
    csv_path = tmp_path / "rois.csv"
    _write_csv(csv_path, [_sample_row(path="/tmp/not_an_roi.png")])
    df = extract_sinker_planktivore_csv(csv_path, mars_base=tmp_path / "MARS")
    assert df.empty


def test_gen_spec_sets_elemental_id():
    spec = gen_spec(
        box=[0.1, 0.2, 0.3, 0.4],
        version_id=1,
        label="Unknown",
        width=1,
        height=1,
        frame_number=0,
        type_id=2,
        media_id=3,
        project_id=4,
        attributes={},
        normalize=False,
        elemental_id=UUID,
    )
    assert spec["elemental_id"] == UUID
    assert spec["x"] == 0.1
    assert spec["width"] == pytest.approx(0.2)


def test_gen_spec_omits_elemental_id_when_missing():
    spec = gen_spec(
        box=[0.1, 0.2, 0.3, 0.4],
        version_id=1,
        label="Unknown",
        width=1,
        height=1,
        frame_number=0,
        type_id=2,
        media_id=3,
        project_id=4,
        attributes={},
        normalize=False,
    )
    assert "elemental_id" not in spec
