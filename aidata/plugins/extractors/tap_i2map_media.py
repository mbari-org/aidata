# aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_i2map_media.py
# Description: Extracts data from i2MAP image meta data

import re
from datetime import datetime
import ephem
import pytz

import pandas as pd
from pathlib import Path

from aidata.logger import info


def extract_media(image_path: Path, max_images: int = None) -> pd.DataFrame:
    """Extracts I2MAP image meta data"""

    # Create a dataframe to store the combined data in an image_path column in sorted order
    images_df = pd.DataFrame()
    images = []
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    for ext in allowed_extensions:
        images.extend(list(image_path.rglob(f"*{ext}")))

    images = [str(image) for image in images]
    images_df["image_path"] = images
    images_df.sort_values(by="image_path")
    if max_images:
        images_df = images_df.head(max_images)

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
    images_df = images_df.groupby("image_path").first().reset_index()
    info(f"Found {len(images_df)} unique images")
    for group, df in images_df.groupby("image_path"):
        image_name = Path(group).name
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
            match = pattern_date1.search(image_name).groups()
            year, month, day, hour, minute, second = map(int, match)
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date2.search(image_name):
            match = pattern_date2.search(image_name).groups()
            year, month, day, hour, minute, second = map(int, match)
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date3.search(image_name):
            match = pattern_date3.search(image_name).groups()
            year, month, day, hour, minute, second = map(int, match)
            year = 2000 + year
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        if pattern_date4.search(image_name):
            match = pattern_date4.search(image_name).groups()
            year, month, day, hour, minute, second = map(int, match)
            year = 2000 + year
            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            day_flag[index] = is_day(dt)
            iso_datetime[index] = dt
        index += 1

    # Add the depth, day, and night columns to the dataframe if they exist
    if len(depth) > 0:
        images_df["depth"] = depth
        images_df["depth"] = images_df["depth"].astype(int)
    if len(day_flag) > 0:
        images_df["is_day"] = day_flag
        images_df["is_day"] = images_df["is_day"].astype(int)
    if len(iso_datetime) > 0:
        images_df["iso_datetime"] = iso_datetime

    return images_df
