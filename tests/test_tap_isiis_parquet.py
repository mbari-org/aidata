# mbari_aidata, Apache-2.0 license
# Filename: tests/test_tap_isiis_parquet.py
# Description: Tests ISIIS parquet localization extraction and dino3 column remapping
from pathlib import Path

import pandas as pd
import pytest

from mbari_aidata.plugins.extractors.tap_planktivore_parquet import extract_ptvr_parquet


def _write_parquet(path: Path, label_column: str = "dino3_v32_v3") -> None:
    frame = pd.DataFrame(
        {
            "filename": [
                "CFE_ISIIS-002-2023-07-12 09-31-32.253_0005_9.83m.jpg",
                "CFE_ISIIS-001-2023-07-12 09-30-36.364_0001_13.2m.jpg",
            ],
            "epoch_seconds": [1689154292.253, 1689154236.364],
            "time": ["2023-07-12 09:31:32.253", "2023-07-12 09:30:36.364"],
            "depth": [9.83, 13.2],
            label_column: ["copepod", "hydromedusa"],
            f"{label_column}-score": [0.91, 0.42],
        }
    )
    frame.to_parquet(path, index=False)


def test_extract_isiis_parquet_remaps_dino_columns(tmp_path: Path):
    """Test that dino3 model columns are remapped to label and score."""
    parquet_path = tmp_path / "isiis.parquet"
    _write_parquet(parquet_path)

    df = extract_ptvr_parquet(parquet_path)

    assert list(df["image_path"]) == [
        "CFE_ISIIS-001-2023-07-12 09-30-36.364_0001_13.2m.jpg",
        "CFE_ISIIS-002-2023-07-12 09-31-32.253_0005_9.83m.jpg",
    ]
    assert list(df["label"]) == ["hydromedusa", "copepod"]
    assert list(df["score"]) == [0.42, 0.91]
    assert list(df["depth"]) == [13.2, 9.83]
    assert "dino3_v32_v3" not in df.columns
    assert "dino3_v32_v3-score" not in df.columns
    assert "filename" not in df.columns


def test_extract_isiis_parquet_accepts_other_dino3_model_names(tmp_path: Path):
    """Test that any dino3-prefixed model name is remapped the same way."""
    parquet_path = tmp_path / "isiis.parquet"
    _write_parquet(parquet_path, label_column="dino3_other_model")

    df = extract_ptvr_parquet(parquet_path)

    assert set(df["label"]) == {"copepod", "hydromedusa"}
    assert "dino3_other_model" not in df.columns
    assert "dino3_other_model-score" not in df.columns


def test_extract_isiis_parquet_reads_a_directory(tmp_path: Path):
    """Test that a directory of parquet files is combined into one frame."""
    first = tmp_path / "a.parquet"
    second = tmp_path / "nested" / "b.parquet"
    second.parent.mkdir()
    _write_parquet(first, label_column="dino3_v32_v3")
    _write_parquet(second, label_column="dino3_v32_v4")

    df = extract_ptvr_parquet(tmp_path)

    assert len(df) == 4
    assert set(df["label"]) == {"copepod", "hydromedusa"}
    assert {"image_path", "label", "score", "depth", "epoch_seconds", "time"} <= set(df.columns)


def test_extract_isiis_parquet_rejects_missing_score_column(tmp_path: Path):
    """Test that a dino3 label column without its score column is rejected."""
    parquet_path = tmp_path / "isiis.parquet"
    pd.DataFrame(
        {
            "filename": ["frame.jpg"],
            "dino3_v32_v3": ["copepod"],
        }
    ).to_parquet(parquet_path, index=False)

    with pytest.raises(ValueError, match="dino3_v32_v3-score"):
        extract_ptvr_parquet(parquet_path)


def test_extract_isiis_parquet_empty_directory(tmp_path: Path):
    """Test that a directory with no parquet files returns an empty frame."""
    assert extract_ptvr_parquet(tmp_path).empty
