# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_i2map_media.py
# Description: Extracts data from i2MAP image meta data

import re
from datetime import datetime
import ephem  # type: ignore
import pytz

import pandas as pd
from pathlib import Path

from mbari_aidata.logger import info
from mbari_aidata.plugins.extractors.media_types import MediaType


def extract_media(media_path: Path, max_images: int = -1) -> pd.DataFrame:
    """Extracts I2MAP image meta data"""

    # Create a dataframe to store the combined data in an media_path column in sorted order
    media_df = pd.DataFrame()
    allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".PNG", ".mp4", ".MP4"]

    # Check if media_path is a txt file containing list of paths
    if media_path.is_file() and media_path.suffix.lower() == '.txt':
        with open(media_path, 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
        media_df["media_path"] = [p for p in paths if
                                  Path(p).suffix.lower() in [ext.lower() for ext in allowed_extensions]]
    elif media_path.is_dir():
        media_df["media_path"] = [str(file) for file in media_path.rglob("*") if
                                  file.suffix.lower() in allowed_extensions]
    elif media_path.is_file():
        media_df["media_path"] = [str(media_path)]
        # Keep only if it has acceptable extension
        media_df = media_df[media_df["media_path"].str.endswith(tuple(allowed_extensions))]

    media_df = media_df.sort_values(by="media_path").reset_index(drop=True)

    if max_images and max_images > 0:
        media_df = media_df.head(max_images)

    # If all .mp4, then set the media type to VIDEO
    if all(media_df["media_path"].str.endswith(".mp4")):
        media_type = MediaType.VIDEO
    else:
        media_type = MediaType.IMAGE

    pattern_date1 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 20161025T184500Z
    pattern_date2 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z\d*mF*")
    pattern_date3 = re.compile(r"(\d{2})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 161025T184500Z
    pattern_date4 = re.compile(r"(\d{2})-(\d{2})-(\d{2})T(\d{2})_(\d{2})_(\d{2})-")  # 16-06-06T16_04_54

    # Grab any additional metadata from the image name, e.g. depth, day/night
    depth = {}
    day_flag = {}
    observer = ephem.Observer()
    iso_datetime = {}
    # Location of the data to cluster - only used if day/night filtering is enabled
    # Monterey Bay
    latitude = "36.7253"
    longitude = "-121.7840"
    observer.lat = latitude
    observer.lon = longitude

    def is_day(utc_dt):
        observer.date = utc_dt
        sun = ephem.Sun(observer)
        if float(sun.alt) > 0:
            return 1
        return 0

    index = 0
    media_df = media_df.groupby("media_path").first().reset_index()
    info(f"Found {len(media_df)} unique media files")
    for group, df in media_df.groupby("media_path"):
        image_name = Path(str(group)).name
        info(image_name)
        for depth_str in [
            "50m",
            "100m",
            "200m",
            "300m",
            "400m",
            "500m",
            "299m",
            "250m",
            "150m",
            "199m",
            "800m",
            "900m",
            "700m",
            "600m",
            "1000m",
        ]:
            if depth_str in image_name:
                depth[index] = int(depth_str.split("m")[0])
                break
        if pattern_date1.search(image_name):
            match = pattern_date1.search(image_name)
            if match is None:
                continue
            year, month, day, hour, minute, second = map(int, match.groups())
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date2.search(image_name):
            match = pattern_date2.search(image_name)
            if match is None:
                continue
            year, month, day, hour, minute, second = map(int, match.groups())
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date3.search(image_name):
            match = pattern_date3.search(image_name)
            if match is None:
                continue
            year, month, day, hour, minute, second = map(int, match.groups())
            year = 2000 + year
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date4.search(image_name):
            match = pattern_date4.search(image_name)
            if match is None:
                continue
            year, month, day, hour, minute, second = map(int, match.groups())
            year = 2000 + year
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        index += 1

    # Add the depth, day, and night columns to the dataframe if they exist
    if len(depth) > 0:
        media_df["depth"] = depth
        media_df["depth"] = media_df["depth"].astype(int)
    if len(day_flag) > 0:
        media_df["is_day"] = day_flag
        media_df["is_day"] = media_df["is_day"].astype(int)
    if len(iso_datetime) > 0:
        if media_type == MediaType.VIDEO: 
            media_df["iso_start_datetime"] = iso_datetime
        else:
            media_df["iso_datetime"] = iso_datetime

    media_df["media_type"] = media_type
    return media_df
