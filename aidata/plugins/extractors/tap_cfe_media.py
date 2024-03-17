# aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_cfe_media.py
# Description: Extracts data from CFE image meta data
from enum import Enum
import re
from datetime import datetime
import pytz

import pandas as pd
from pathlib import Path

from aidata.logger import info


# Add an enum class for the instrument types ISIIS, SES, SINKER, MINION_FLUX and SNOW_CAM
class Instrument(Enum):
    ISIIS = "ISIIS"
    SES = "SES"
    SINKER = "SINKER"
    MINION_FLUX = "MINION_FLUX"
    SNOW_CAM = "SNOW_CAM"


def extract_media(image_path: Path, max_images: int = None) -> pd.DataFrame:
    """Extracts data CFE image meta data"""

    # Create a dataframe to store the combined data in an image_path column in sorted order
    images_df = pd.DataFrame()
    images = []
    allowed_extensions = [".png"]
    for ext in allowed_extensions:
        images.extend(list(image_path.rglob(f"*{ext}")))

    images = [str(image) for image in images]
    images_df["image_path"] = images
    images_df.sort_values(by="image_path")
    if max_images:
        images_df = images_df.iloc[:max_images]

    # 'CFE_ISIIS-010-2024-01-26T10-14-07.102Z_0835.png'
    pattern_date = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}.\d{3}Z")  # 2016-06-06T16_04_54
    pattern_instrument = re.compile(r"(.+?)\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}")  # CFE_ISIIS-010-
    pattern_frame = re.compile(r"_(\d{4}).png")  # 0835.png

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    instrument_type = {}
    index = 0
    images_df = images_df.groupby("image_path").first().reset_index()
    info(f"Found {len(images_df)} unique images")
    fps = 17
    for group, df in images_df.groupby("image_path"):
        image_name = Path(group).name
        info(image_name)
        if pattern_date.search(image_name):
            match = pattern_date.search(image_name)
            datetime_str = match[0]
            dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H-%M-%S.%fZ")
            dt_utc = pytz.utc.localize(dt)
            iso_datetime[index] = dt_utc
        if pattern_instrument.search(image_name):
            match = pattern_instrument.search(image_name).groups()
            instrument = match[0]
            instrument_type[index] = instrument[:-1]  # Remove trailing - from instrument type
        if pattern_frame.search(image_name):
            match = pattern_frame.search(image_name).groups()
            increment_seconds = int(int(match[0]) / fps)
            # Add the increment seconds to the iso datetime
            iso_datetime[index] = iso_datetime[index] + pd.Timedelta(seconds=increment_seconds)
        index += 1

    if len(instrument_type) == 0:
        raise ValueError("No instrument type found in image names")
    if len(iso_datetime) == 0:
        raise ValueError("No iso datetime found in image names")

    images_df["instrument"] = instrument_type
    images_df["iso_datetime"] = iso_datetime

    return images_df
