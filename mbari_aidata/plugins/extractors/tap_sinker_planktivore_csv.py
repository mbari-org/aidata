# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_sinker_planktivore_csv.py
# Description: Extracts mosaic media paths and boxes from SINKER Planktivore ROI CSVs
import re
from pathlib import Path
from typing import Callable, Optional, Tuple

import pandas as pd
from PIL import Image

from mbari_aidata.logger import info, warn
from mbari_aidata.plugins.extractors.media_types import MediaType

# Mosaic JPEGs live under this root: /mnt/SINKER/MARS/{instrument}/{YYYY}/{MM}/{DD}/{HH}/{stem}.jpeg
MARS_BASE_PATH = Path("/mnt/SINKER/MARS")
MOSAIC_RELATIVE_DEPTH = 5
ROI_NAME_RE = re.compile(r"^(?P<stem>.+)_(?P<x>\d+)_(?P<y>\d+)_(?P<w>\d+)_(?P<h>\d+)_(?P<roi_idx>\d{4})\.\w+$")
SINKER_REQUIRED_COLUMNS = {"uuid", "path", "timestamp"}
ImageSizeFn = Callable[[Path], Tuple[int, int]]


def is_sinker_planktivore_csv(csv_path: Path) -> bool:
    """Return True if the CSV header matches the SINKER Planktivore mosaic ROI format."""
    if csv_path.is_dir():
        csvs = list(csv_path.rglob("*.csv"))
        if not csvs:
            return False
        csv_path = csvs[0]
    if csv_path.suffix.lower() != ".csv":
        return False
    try:
        columns = set(pd.read_csv(csv_path, nrows=0).columns)
    except Exception:
        return False
    return SINKER_REQUIRED_COLUMNS.issubset(columns)


def mosaic_path_from_roi_path(roi_path: Path, stem: str, mars_base: Path = MARS_BASE_PATH) -> Optional[Path]:
    """Map an extracted-ROI path to the source mosaic JPEG under the MARS root."""
    parts = list(roi_path.parts)
    if "extracted_rois" not in parts:
        return None
    idx = parts.index("extracted_rois")
    start = max(0, idx - MOSAIC_RELATIVE_DEPTH)
    relative = Path(*parts[start:idx])
    if not relative.parts:
        return None
    return mars_base / relative / f"{stem}.jpeg"


def parse_roi_filename(name: str) -> Optional[dict]:
    """Parse `{stem}_{x}_{y}_{w}_{h}_{roi_idx:04d}` from an ROI crop filename."""
    match = ROI_NAME_RE.match(name)
    if not match:
        return None
    return {
        "stem": match.group("stem"),
        "x": int(match.group("x")),
        "y": int(match.group("y")),
        "w": int(match.group("w")),
        "h": int(match.group("h")),
        "roi_idx": int(match.group("roi_idx")),
    }


def _read_image_size(image_path: Path) -> Tuple[int, int]:
    with Image.open(image_path) as img:
        return img.size


def _load_csvs(csv_path: Path) -> pd.DataFrame:
    if csv_path.is_dir():
        frames = []
        for path in sorted(csv_path.rglob("*.csv")):
            try:
                frames.append(pd.read_csv(path))
            except Exception as exc:
                warn(f"Error reading {path}: {exc}")
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
    return pd.read_csv(csv_path)


def _parse_rows(df: pd.DataFrame, mars_base: Path) -> pd.DataFrame:
    parsed = []
    for _, row in df.iterrows():
        roi_path = Path(str(row["path"]))
        roi_fields = parse_roi_filename(roi_path.name)
        if roi_fields is None:
            warn(f"Could not parse ROI filename: {roi_path.name}")
            continue
        media_path = mosaic_path_from_roi_path(roi_path, roi_fields["stem"], mars_base=mars_base)
        if media_path is None:
            warn(f"Could not reconstruct mosaic path from {roi_path}")
            continue
        record = row.to_dict()
        record["pixel_x"] = roi_fields["x"]
        record["pixel_y"] = roi_fields["y"]
        record["pixel_w"] = roi_fields["w"]
        record["pixel_h"] = roi_fields["h"]
        record["roi_idx"] = roi_fields["roi_idx"]
        record["stem"] = roi_fields["stem"]
        record["media_path"] = media_path.as_posix()
        record["image_path"] = media_path.as_posix()
        record["elemental_id"] = str(row["uuid"])
        record["iso_datetime"] = pd.to_datetime(row["timestamp"], utc=True)
        parsed.append(record)
    if not parsed:
        return pd.DataFrame()
    return pd.DataFrame(parsed)


def extract_sinker_planktivore_csv(
    csv_path: Path,
    mars_base: Path = MARS_BASE_PATH,
    image_size_fn: Optional[ImageSizeFn] = None,
) -> pd.DataFrame:
    """Extract normalized boxes and mosaic paths from a SINKER Planktivore ROI CSV."""
    raw = _load_csvs(csv_path)
    if raw.empty:
        return raw
    if not SINKER_REQUIRED_COLUMNS.issubset(raw.columns):
        warn(f"CSV {csv_path} is missing required columns {SINKER_REQUIRED_COLUMNS}")
        return pd.DataFrame()

    df = _parse_rows(raw, mars_base)
    if df.empty:
        return df

    size_fn = image_size_fn or _read_image_size
    size_cache: dict = {}
    rows = []
    for _, row in df.iterrows():
        media_path = Path(row["media_path"])
        key = media_path.as_posix()
        try:
            if key not in size_cache:
                size_cache[key] = size_fn(media_path)
            image_width, image_height = size_cache[key]
        except Exception as exc:
            warn(f"Could not read image size for {media_path}: {exc}")
            continue
        rec = row.to_dict()
        rec["image_width"] = image_width
        rec["image_height"] = image_height
        rec["x"] = rec["pixel_x"] / image_width
        rec["y"] = rec["pixel_y"] / image_height
        rec["xx"] = (rec["pixel_x"] + rec["pixel_w"]) / image_width
        rec["xy"] = (rec["pixel_y"] + rec["pixel_h"]) / image_height
        rec["label"] = "Unknown"
        rec["score"] = 1.0
        rec["media_type"] = MediaType.IMAGE
        rows.append(rec)

    if not rows:
        return pd.DataFrame()
    result = pd.DataFrame(rows)
    info(f"Extracted {len(result)} SINKER Planktivore boxes from {csv_path}")
    return result


def extract_media(
    media_path: Path,
    max_images: Optional[int] = None,
    mars_base: Path = MARS_BASE_PATH,
) -> pd.DataFrame:
    """Extract unique mosaic images referenced by a SINKER Planktivore ROI CSV."""
    raw = _load_csvs(media_path)
    if raw.empty:
        return raw
    df = _parse_rows(raw, mars_base)
    if df.empty:
        return df

    media_df = df.drop_duplicates(subset=["media_path"]).copy().reset_index(drop=True)
    media_df["media_type"] = MediaType.IMAGE
    if max_images and max_images > 0:
        media_df = media_df.iloc[:max_images]
    info(f"Found {len(media_df)} unique mosaic images in {media_path}")
    return media_df[["media_path", "iso_datetime", "media_type"]].reset_index(drop=True)
