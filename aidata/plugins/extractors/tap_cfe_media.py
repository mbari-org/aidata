# aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_cfe_media.py
# Description: Extracts data from CFE image meta data
from enum import Enum
import re
from datetime import datetime
from typing import Optional

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


def extract_media(image_path: Path, max_images: Optional[int] = None) -> pd.DataFrame:
    """Extracts data CFE image meta data"""

    # Create a dataframe to store the combined data in an image_path column in sorted order
    images_df = pd.DataFrame()
    if image_path.is_dir():
        images_df["image_path"] = [f.as_posix() for f in image_path.rglob("*")]
    elif image_path.is_file():
        images_df["image_path"] = [image_path.as_posix()]
    images_df.sort_values(by="image_path")
    if 0 < max_images < len(images_df):
        images_df = images_df.iloc[:max_images]

    # 'CFE_ISIIS-010-2024-01-26 10-14-07.102_0835_8.3m.png'
    pattern = re.compile(r"CFE_(.*?)-(\d+)-(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.\d{3})_(\d{4})_(\d+\.\d+)m\.(png|jpg|jpeg|JPEG|PNG)")

    index = 0
    images_df = images_df.groupby("image_path").first().reset_index()

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    instrument_type = {}
    depth = {}
    info(f"Found {len(images_df)} unique images")
    fps = 17
    for group, df in images_df.groupby("image_path"):
        image_name = Path(str(group)).name
        info(image_name)
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

    if len(instrument_type) == 0:
        raise ValueError("No instrument type found in CFE image names")
    if len(iso_datetime) == 0:
        raise ValueError("No iso datetime found in image names")
    if len(depth) == 0:
        raise ValueError("No depth found in image names")

    images_df["instrument"] = instrument_type
    images_df["iso_datetime"] = iso_datetime
    images_df["depth"] = depth
    return images_df