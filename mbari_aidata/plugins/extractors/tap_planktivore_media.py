# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_planktivore_media.py
# Description: Extracts data from CFE image meta data
import re
from datetime import datetime
from typing import Optional

import pytz

import pandas as pd
from pathlib import Path

from mbari_aidata.logger import info
from mbari_aidata.plugins.extractors.media_types import MediaType


def extract_media(media_path: Path, max_images: Optional[int] = None) -> pd.DataFrame:
    """Extracts Planktivore image meta data"""

    # Create a dataframe to store the combined data in an media_path column in sorted order
    images_df = pd.DataFrame()

    allowed_extensions = [".png", ".jpg"]
    images_df["media_path"] = [str(file) for file in media_path.rglob("*") if file.suffix.lower() in allowed_extensions]
    images_df.sort_values(by="media_path")
    if 0 < max_images < len(images_df):
        images_df = images_df.iloc[:max_images]

    # 'LRAH13_20240430T123018.838913Z_PTVR02HM_283109_3_1202_264_0_272_164_0.jpg*'
    pattern = re.compile(r'\d{8}T\d{6}\.\d+Z')

    # Grab any additional metadata from the image name,
    iso_datetime = {}
    info(f"Found {len(images_df)} unique images")
    for index, row in images_df.iterrows():
        image_name = row["media_path"]
        matches = re.findall(pattern, image_name)
        if matches:
            datetime_str = matches[0]
            dt = datetime.strptime(datetime_str, "%Y%m%dT%H%M%S.%fZ")
            dt_utc = pytz.utc.localize(dt)
            iso_datetime[index] = dt_utc

    images_df["iso_datetime"] = iso_datetime
    images_df["media_type"] =  MediaType.IMAGE
    return images_df
