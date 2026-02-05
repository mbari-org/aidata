# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractors/tap_vars_media.py
# Description: Extracts media data for loading into Tator

import re
from datetime import datetime
import pytz

import pandas as pd
from pathlib import Path

from mbari_aidata.logger import info
from mbari_aidata.plugins.extractors.media_types import MediaType


def extract_media(media_path: Path, max_images: int = -1) -> pd.DataFrame:
    """Extracts VARS image metadata"""

    # Create a dataframe to store the combined data
    media_df = pd.DataFrame()
    allowed_extensions = [".jpg"]

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
        media_df = media_df[media_df["media_path"].str.endswith(tuple(allowed_extensions))]

    media_df = media_df.sort_values(by="media_path").reset_index(drop=True)

    if max_images and max_images > 0:
        media_df = media_df.head(max_images)

    media_type = MediaType.IMAGE

    # Pattern for VARS images: <mission>_<YYYYMMDD>_<HHMMSS>_<millis>.jpg
    pattern_vars = re.compile(r"^(.+?)_(\d{8})_(\d{6})_(\d+)\.jpg$")
    # Pattern for UUID images
    pattern_uuid = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jpg$", re.IGNORECASE)

    missions = {}
    iso_datetimes = {}
    elapsed_times = {}

    media_df = media_df.groupby("media_path").first().reset_index()
    info(f"Found {len(media_df)} unique media files")

    for index, row in media_df.iterrows():
        image_name = Path(row["media_path"]).name
        info(image_name)

        # Check if it's a UUID image
        if pattern_uuid.match(image_name):
            missions[index] = "Unknown"
            iso_datetimes[index] = None
            elapsed_times[index] = 0
            continue

        # Try to match VARS pattern
        match = pattern_vars.match(image_name)
        if match:
            mission, date_str, time_str, millis = match.groups()
            missions[index] = mission
            elapsed_times[index] = int(millis)

            # Parse datetime
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:6])

            dt = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
            iso_datetimes[index] = dt

    # Add extracted columns to dataframe
    if missions:
        media_df["mission"] = pd.Series(missions)
    if iso_datetimes:
        media_df["iso_datetime"] =  pd.Series(iso_datetimes).dropna()
    if elapsed_times:
        media_df["index_elapsed_time_millis"] = pd.Series(elapsed_times).astype(int)

    media_df["media_type"] = media_type
    return media_df
