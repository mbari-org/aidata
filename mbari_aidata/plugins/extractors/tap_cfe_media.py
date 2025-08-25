# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_cfe_media.py
# Description: Extracts data from CFE image/video meta data
from enum import Enum
import re
from datetime import datetime
from typing import Optional

import pytz

import pandas as pd
from pathlib import Path

from mbari_aidata.logger import info, exception
from mbari_aidata.plugins.extractors.media_types import MediaType


# Add an enum class for the instrument types ISIIS, SES, SINKER, MINION_FLUX and SNOW_CAM
class Instrument(Enum):
    ISIIS = "ISIIS"
    SES = "SES"
    SINKER = "SINKER"
    MINION_FLUX = "MINION_FLUX"
    SNOW_CAM = "SNOW_CAM"


def extract_media(media_path: Path, max_images: Optional[int] = None) -> pd.DataFrame:

    df_images = extract_images(media_path, max_images)
    df_videos = extract_videos(media_path, max_images)
    df = pd.concat([df_images, df_videos], ignore_index=True)
    return df


def extract_videos(media_path: Path, max_videos: Optional[int] = None) -> pd.DataFrame:
    """Extracts data CFE video meta data"""

    # Create a dataframe to store the combined data in a media_path column in sorted order
    df = pd.DataFrame()
    acceptable_extensions = ["mp4"]

    if media_path.is_file() and media_path.suffix.lower() == '.txt':
        with open(media_path, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
        df["media_path"] = [p for p in paths if Path(p).suffix.lower().lstrip('.') in [ext.lower() for ext in acceptable_extensions]]
    elif media_path.is_dir():
        df["media_path"] = [f.as_posix() for f in media_path.rglob("*.mp4")]
    elif media_path.is_file():
        df["media_path"] = [media_path.as_posix()]
        df = df[df["media_path"].str.endswith(tuple(acceptable_extensions))]

    if 0 < max_videos < len(df):
        df = df.iloc[:max_videos] # Limit the number of videos to process

    # CFE_ISIIS-010-2024-01-26 10-14-07.102_0835.mp4
    # CFE_ISIIS-029-2025-04-05 10-52-46.523.mp4
    pattern = re.compile(r"CFE_(.*?)-(\d+)-(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.\d{3})\.mp4")

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    instrument_type = {}
    info(f"Found {len(df)} unique videos")
    if len(df) == 0:
        return pd.DataFrame()
    try:
        for index, row in df.iterrows():
            image_name = Path(str(row.media_path)).name
            info(image_name)
            matches = re.findall(pattern, image_name)
            if matches:
                instrument, _, datetime_str = matches[0]
                datetime_str = datetime_str + "Z"
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H-%M-%S.%fZ")
                dt_utc = pytz.utc.localize(dt)
                iso_datetime[index] = dt_utc
                instrument_type[index] = instrument
                iso_datetime[index] = iso_datetime[index]
                index += 1

        if len(instrument_type) == 0:
            raise ValueError("No instrument type found in CFE video names")
        if len(iso_datetime) == 0:
            raise ValueError("No iso datetime found in video names")

        df["instrument"] = instrument_type
        df["iso_start_datetime"] = iso_datetime
        df["media_type"] = MediaType.VIDEO
        return df
    except Exception as e:
        exception(f"Error extracting video metadata: {e}")
        return pd.DataFrame()


def extract_images(media_path: Path, max_images: Optional[int] = None) -> pd.DataFrame:
    """Extracts data CFE image meta data from Path or txt file with list of paths"""

    # Create a dataframe to store the combined data in an media_path column in sorted order
    df = pd.DataFrame()
    acceptable_extensions = ["png", "jpg", "jpeg", "JPEG", "PNG"]

    # Check if media_path is a txt file containing list of paths
    if media_path.is_file() and media_path.suffix.lower() == '.txt':
        with open(media_path, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
        df["media_path"] = [p for p in paths if
                            Path(p).suffix.lower().lstrip('.') in [ext.lower() for ext in acceptable_extensions]]
    elif media_path.is_dir():
        df["media_path"] = [f.as_posix() for f in media_path.rglob("*")]
        # Keep only the images with the acceptable extensions
        df = df[df["media_path"].str.endswith(tuple(acceptable_extensions))]
    elif media_path.is_file():
        df["media_path"] = [media_path.as_posix()]
        # Keep only if it has acceptable extension
        df = df[df["media_path"].str.endswith(tuple(acceptable_extensions))]

    df = df.sort_values(by="media_path").reset_index(drop=True)

    if 0 < max_images < len(df):
        df = df.iloc[:max_images]

    if len(df) == 0:
        return pd.DataFrame()

    # CFE_ISIIS-010-2024-01-26 10-14-07.102_0835_8.3m.png
    pattern = re.compile(r"CFE_(.*?)-(\d+)-(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.\d{3})_(\d{4})_(\d+\.\d+)m\.(png|jpg|jpeg)", re.IGNORECASE)
    # or CFE_ISIIS-010-2024-01-26 10-14-07.102_0835.png
    pattern_no_depth = re.compile(r"CFE_(.*?)-(\d+)-(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.\d{3})_(\d{4})\.(png|jpg|jpeg)", re.IGNORECASE)

    index = 0
    # Grab any additional metadata from the image name,
    iso_datetime = {}
    instrument_type = {}
    depth = {}
    info(f"Found {len(df)} unique images")
    fps = 17
    try:
        df = df.groupby("media_path").first().reset_index()
        for group, df in df.groupby("media_path"):
            image_name = Path(str(group)).name
            info(f'Processing image: {image_name}')
            matches = re.findall(pattern, image_name)
            if matches:
                instrument, _, datetime_str, frame_num, depth_str, ext = matches[0]
                datetime_str = datetime_str + "Z"
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H-%M-%S.%fZ")
                dt_utc = pytz.utc.localize(dt)
                iso_datetime[index] = dt_utc
                instrument_type[index] = instrument
                depth[index] = float(depth_str)
                increment_mseconds = int(int(frame_num) * 1e6 / fps)
                iso_datetime[index] = iso_datetime[index] + pd.Timedelta(microseconds=increment_mseconds)
                index += 1
            else:
                matches = re.findall(pattern_no_depth, image_name)
                if matches:
                    instrument, _, datetime_str, frame_num, ext = matches[0]
                    datetime_str = datetime_str + "Z"
                    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H-%M-%S.%fZ")
                    dt_utc = pytz.utc.localize(dt)
                    iso_datetime[index] = dt_utc
                    instrument_type[index] = instrument
                    depth[index] = None
                    increment_mseconds = int(int(frame_num) * 1e6 / fps)
                    iso_datetime[index] = iso_datetime[index] + pd.Timedelta(microseconds=increment_mseconds)
                    index += 1


        if len(instrument_type) == 0:
            raise ValueError("No instrument type found in CFE image names")
        if len(iso_datetime) == 0:
            raise ValueError("No iso datetime found in image names")
        if len(depth) == 0:
            raise ValueError("No depth found in image names")

        df["instrument"] = instrument_type
        df["iso_datetime"] = iso_datetime
        df["depth"] = depth
        df["media_type"] = MediaType.IMAGE
        return df
    except Exception as e:
        exception(f"Error extracting image metadata: {e}")
        return pd.DataFrame()
