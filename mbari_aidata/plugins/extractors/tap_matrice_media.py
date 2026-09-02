# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_matrice_media.py
# Description: Extracts GPS EXIF and DJI XMP relative altitude from Matrice _W.JPG images and _Z.mp4 videos
from datetime import datetime
from urllib.request import urlopen

import pandas as pd
from pathlib import Path
import piexif  # type: ignore
import pytz
import re

from mbari_aidata.logger import info, err
from mbari_aidata.plugins.extractors.media_types import MediaType

IMAGE_CAMERA_SUFFIX = "_W"
VIDEO_CAMERA_SUFFIX = "_Z"
IMAGE_EXTENSIONS = (".jpg", ".jpeg")
VIDEO_EXTENSIONS = (".mp4",)
# DJI_YYYYMMDDHHMMSS_NNNN_Z.mp4
_DJI_FILENAME_DT = re.compile(r"DJI_(\d{14})_", re.IGNORECASE)
_RELATIVE_ALTITUDE = re.compile(br'drone-dji:RelativeAltitude="([+-]?\d+(?:\.\d+)?)"')
_HTTP_EXIF_BYTES = 200_000


def _path_name(media_path: str) -> str:
    """Return the filename, ignoring URL query strings."""
    return Path(media_path.split("?")[0]).name


def _is_matrice_image(media_path: str) -> bool:
    name = _path_name(media_path)
    return Path(name).stem.upper().endswith(IMAGE_CAMERA_SUFFIX) and Path(name).suffix.lower() in IMAGE_EXTENSIONS


def _is_matrice_video(media_path: str) -> bool:
    name = _path_name(media_path)
    return Path(name).stem.upper().endswith(VIDEO_CAMERA_SUFFIX) and Path(name).suffix.lower() in VIDEO_EXTENSIONS


def _decode_gps_ref(ref) -> str:
    if isinstance(ref, bytes):
        return ref.decode("utf-8", errors="ignore").strip("\x00").strip()
    return str(ref).strip()


def _rational_to_float(value) -> float:
    if isinstance(value, tuple) and len(value) == 2:
        num, den = value
        return float(num) / float(den) if den else 0.0
    return float(value)


def dms_to_decimal(dms, ref) -> float:
    """Convert EXIF GPS DMS plus N/S/E/W ref to signed decimal degrees."""
    decimal = _rational_to_float(dms[0]) + _rational_to_float(dms[1]) / 60.0 + _rational_to_float(dms[2]) / 3600.0
    if _decode_gps_ref(ref).upper()[:1] in ("S", "W"):
        decimal = -decimal
    return decimal


def relative_altitude_from_xmp(data: bytes) -> float | None:
    """Return DJI XMP RelativeAltitude in meters (height above takeoff), if present."""
    match = _RELATIVE_ALTITUDE.search(data)
    if not match:
        return None
    return float(match.group(1))


def gps_altitude(gps: dict) -> float:
    """Return unsigned GPSAltitude in meters (fallback when XMP RelativeAltitude is missing)."""
    return _rational_to_float(gps[piexif.GPSIFD.GPSAltitude])


def datetime_from_dji_filename(media_path: str) -> datetime | None:
    """Parse DJI_YYYYMMDDHHMMSS from a Matrice filename as UTC (camera local time, same as Sony)."""
    match = _DJI_FILENAME_DT.search(_path_name(media_path))
    if not match:
        return None
    dt = datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
    return pytz.utc.localize(dt)


def _collect_paths(media_path: Path, matcher) -> pd.DataFrame:
    """Collect media paths from a directory, file, or txt listing."""
    paths: list[str] = []
    if media_path.is_file() and media_path.suffix.lower() == ".txt":
        with open(media_path, "r") as f:
            raw = [line.strip() for line in f if line.strip()]
        paths = [p for p in raw if matcher(p)]
    elif media_path.is_dir():
        paths = [str(f) for f in media_path.rglob("*") if matcher(str(f))]
    elif media_path.is_file() and matcher(str(media_path)):
        paths = [str(media_path)]

    df = pd.DataFrame({"media_path": paths})
    if df.empty:
        return df
    return df.sort_values(by="media_path").reset_index(drop=True)


def _read_media_bytes(media_path: str) -> bytes:
    """Read enough of a local file or HTTP URL for EXIF plus DJI XMP."""
    if str(media_path).startswith("http"):
        try:
            partial_data = urlopen(media_path).read(_HTTP_EXIF_BYTES)
            if relative_altitude_from_xmp(partial_data) is not None:
                return partial_data
            info("RelativeAltitude not in partial read, reading full image...")
            return urlopen(media_path).read()
        except Exception as partial_error:
            info(f"Partial read failed ({str(partial_error)}), reading full image...")
            return urlopen(media_path).read()
    return Path(media_path).read_bytes()


def _gps_and_date_from_exif(data: bytes) -> tuple[float, float, float, datetime]:
    """Return latitude, longitude, relative altitude, and UTC datetime from EXIF GPS + DJI XMP."""
    exif = piexif.load(data)
    date_time_str = exif["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8").strip()
    dt_utc = pytz.utc.localize(datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S"))
    gps = exif["GPS"]
    lat = dms_to_decimal(gps[piexif.GPSIFD.GPSLatitude], gps[piexif.GPSIFD.GPSLatitudeRef])
    lon = dms_to_decimal(gps[piexif.GPSIFD.GPSLongitude], gps[piexif.GPSIFD.GPSLongitudeRef])
    alt = relative_altitude_from_xmp(data)
    if alt is None:
        alt = gps_altitude(gps)
    return lat, lon, alt, dt_utc


def extract_media(media_path: Path, max_images: int = -1) -> pd.DataFrame:
    """Extract DJI Matrice image/video metadata (GPS EXIF on images, filename time on videos)."""
    df_images = extract_images(media_path, max_images)
    df_videos = extract_videos(media_path, max_images)
    info(f"Found {len(df_images)} images and {len(df_videos)} videos")
    frames = [df for df in (df_images, df_videos) if not df.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def extract_images(media_path: Path, max_images: int = -1) -> pd.DataFrame:
    """Extract latitude/longitude from GPS EXIF and altitude from XMP RelativeAltitude."""
    images_df = _collect_paths(media_path, _is_matrice_image)
    if max_images > 0:
        images_df = images_df.head(max_images)

    info(f"Found {len(images_df)} unique images")
    if images_df.empty:
        return images_df

    info(f"Reading EXIF GPS from {len(images_df)} Matrice images")
    altitude: list[float] = []
    latitude: list[float] = []
    longitude: list[float] = []
    date: list[datetime] = []
    failed_indexes: list = []
    sorted_df = images_df.sort_values(by="media_path")
    for i, row in sorted_df.iterrows():
        info(f"Reading EXIF data in {row.media_path}")
        try:
            lat, lon, alt, dt_utc = _gps_and_date_from_exif(_read_media_bytes(row.media_path))
            latitude.append(lat)
            longitude.append(lon)
            altitude.append(alt)
            date.append(dt_utc)
        except Exception as e:
            err(f"Failed to read EXIF from {row.media_path}: {str(e)}")
            failed_indexes.append(i)

    modified_df = sorted_df.drop(failed_indexes).copy()
    modified_df["altitude"] = altitude
    modified_df["latitude"] = latitude
    modified_df["longitude"] = longitude
    modified_df["date"] = date
    modified_df["media_type"] = MediaType.IMAGE
    info(f"Extracted GPS from {len(modified_df)} of {len(sorted_df)} images")
    return modified_df


def extract_videos(media_path: Path, max_videos: int = -1) -> pd.DataFrame:
    """Extract iso_start_datetime from DJI Matrice _Z.mp4 filenames."""
    videos_df = _collect_paths(media_path, _is_matrice_video)
    if max_videos > 0:
        videos_df = videos_df.head(max_videos)

    info(f"Found {len(videos_df)} unique videos")
    if videos_df.empty:
        return videos_df

    iso_start: list[datetime] = []
    failed_indexes: list = []
    sorted_df = videos_df.sort_values(by="media_path")
    for i, row in sorted_df.iterrows():
        dt_utc = datetime_from_dji_filename(row.media_path)
        if dt_utc is None:
            err(f"Failed to parse DJI datetime from {row.media_path}")
            failed_indexes.append(i)
            continue
        iso_start.append(dt_utc)

    modified_df = sorted_df.drop(failed_indexes).copy()
    modified_df["iso_start_datetime"] = iso_start
    modified_df["media_type"] = MediaType.VIDEO
    return modified_df
