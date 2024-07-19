# aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_cfe_media.py
# Description: Extracts data from CFE image meta data
from enum import Enum
import re
from datetime import datetime
from typing import Optional, List

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
    allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".PNG"]
    images_df["image_path"] = [str(file) for file in image_path.rglob("*") if file.suffix.lower() in allowed_extensions]
    images_df.sort_values(by="image_path")
    if max_images:
        images_df = images_df.iloc[:max_images]

    # 'CFE_ISIIS-010-2024-01-26 10-14-07.102_0835.png'
    pattern = re.compile(r"CFE_(.*?)-(\d+)-(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}\.\d{3})_(\d{4})")

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    instrument_type = {}
    index = 0
    images_df = images_df.groupby("image_path").first().reset_index()
    info(f"Found {len(images_df)} unique images")
    fps = 17
    for group, df in images_df.groupby("image_path"):
        image_name = Path(str(group)).name
        #: Argument 1 to "Path" has incompatible type "str | bytes | date | datetime | timedelta | datetime64 | timedelta64 | bool | int | float | Timestamp | Timedelta | complex"; expected "str | PathLike[str]"  [arg-type]
        # aidata/generators/coco.py:11: error: Skipping analyzi
        info(image_name)
        matches = re.findall(pattern, image_name)
        if matches:
            instrument, _, datetime_str, frame_num = matches[0]
            datetime_str = datetime_str + "Z"
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H-%M-%S.%fZ")
            dt_utc = pytz.utc.localize(dt)
            iso_datetime[index] = dt_utc
            instrument_type[index] = instrument
            increment_mseconds = int(int(frame_num) * 1e6 / fps)
            iso_datetime[index] = iso_datetime[index] + pd.Timedelta(microseconds=increment_mseconds)
            index += 1

    if len(instrument_type) == 0:
        raise ValueError("No instrument type found in CFE image names")
    if len(iso_datetime) == 0:
        raise ValueError("No iso datetime found in image names")

    if max_images:
        images_df = images_df.head(max_images)

    images_df["instrument"] = instrument_type
    images_df["iso_datetime"] = iso_datetime
    return images_df
