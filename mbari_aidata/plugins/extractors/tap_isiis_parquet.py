# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_isiis_parquet.py
# Description: Extracts localizations from ISIIS parquet files for loading into Tator

from pathlib import Path

import pandas as pd
import tqdm

from mbari_aidata.logger import err

DINO_PREFIX = "dino3"
SCORE_SUFFIX = "-score"


def _dino_label_and_score_columns(columns) -> tuple[str, str]:
    """Return the model label column and its matching score column.

    The model name varies, but both columns share the ``dino3`` prefix.
    The score column is the label column name plus ``-score``.
    """
    names = [str(column) for column in columns]
    label_cols = [
        name
        for name in names
        if name.lower().startswith(DINO_PREFIX) and not name.lower().endswith(SCORE_SUFFIX)
    ]
    if len(label_cols) != 1:
        raise ValueError(
            f"Expected one {DINO_PREFIX}* label column, found {label_cols or 'none'}"
        )

    label_col = label_cols[0]
    score_col = f"{label_col}{SCORE_SUFFIX}"
    if score_col not in names:
        raise ValueError(
            f"Expected score column {score_col!r} alongside label column {label_col!r}"
        )
    return label_col, score_col


def _normalize_isiis_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Remap ISIIS parquet columns onto the localization dataframe schema."""
    if "filename" not in df.columns:
        raise ValueError("ISIIS parquet is missing required column 'filename'")

    label_col, score_col = _dino_label_and_score_columns(df.columns)
    normalized = df.rename(
        columns={
            "filename": "image_path",
            label_col: "label",
            score_col: "score",
        }
    )
    normalized["score"] = pd.to_numeric(normalized["score"], errors="coerce")
    return normalized


def extract_isiis_parquet(parquet_path: Path) -> pd.DataFrame:
    """Extract localizations from an ISIIS parquet file or a directory of them.

    Model columns such as ``dino3_v32_v3`` and ``dino3_v32_v3-score`` are
    remapped to ``label`` and ``score``. ``filename`` is remapped to
    ``image_path``. Other columns (for example ``epoch_seconds``, ``time``,
    and ``depth``) are left unchanged so they can be mapped as box attributes.
    """
    if parquet_path.is_dir():
        frames = []
        for det_path in tqdm.tqdm(sorted(parquet_path.rglob("*.parquet")), desc="Reading ISIIS parquet"):
            try:
                frames.append(_normalize_isiis_frame(pd.read_parquet(det_path)))
            except Exception as e:
                err(f"Error reading {det_path}: {e}")
                continue
        if len(frames) == 0:
            return pd.DataFrame()
        combined_df = pd.concat(frames, ignore_index=True)
    else:
        combined_df = _normalize_isiis_frame(pd.read_parquet(parquet_path))

    if len(combined_df) == 0:
        return combined_df

    return combined_df.sort_values(by="image_path").reset_index(drop=True)
