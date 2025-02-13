# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/tap_sony_media.py
# Description: Extracts data from SONY image meta data
from datetime import datetime

import pandas as pd
from pathlib import Path
import piexif  # type: ignore
import pytz

from mbari_aidata.logger import info, err
from mbari_aidata.plugins.extractors.media_types import MediaType


def extract_media(media_path: Path, max_images: int = -1) -> pd.DataFrame:
    """Extracts SONY image meta data"""

    # Create a dataframe to store the combined data in an image_path column in sorted order
    images_df = pd.DataFrame()

    allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".PNG"]
    images_df["media_path"] = [str(file) for file in media_path.rglob("*") if file.suffix.lower() in allowed_extensions]
    images_df.sort_values(by="media_path")
    if max_images > 0:
        images_df = images_df.head(max_images)

    # Check for empty dataframe
    if images_df.empty:
        info("No images found")
        return images_df

    # Read in the exif data from the image
    info(f"Reading exif data from {len(images_df)} images")

    make = []
    model = []
    altitude = []
    latitude = []
    longitude = []
    date = []
    failed_indexes = []
    sorted_df = images_df.sort_values(by="media_path")
    for i, row in sorted_df.iterrows():
        info(f"Reading EXIF data in {row.media_path}")
        try:
            exif = piexif.load(row.media_path)
            # Get the date and time the image was taken
            date_time_str = exif["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
            dt = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
            dt_utc = pytz.utc.localize(dt)
            date.append(dt_utc)
            # Get the latitude and longitude the image was taken
            lat = exif["GPS"][piexif.GPSIFD.GPSLatitude]
            lon = exif["GPS"][piexif.GPSIFD.GPSLongitude]
            # Convert the latitude and longitude to decimal degrees
            lat = lat[0][0] / lat[0][1] + lat[1][0] / lat[1][1] / 60 + lat[2][0] / lat[2][1] / 3600
            lon = lon[0][0] / lon[0][1] + lon[1][0] / lon[1][1] / 60 + lon[2][0] / lon[2][1] / 3600
            # Convert the latitude and longitude to negative if necessary
            if exif["GPS"][piexif.GPSIFD.GPSLatitudeRef] == "S":
                lat = -lat
                # if exif['GPS'][piexif.GPSIFD.GPSLongitudeRef] == 'W':
                lon = -lon
            latitude.append(lat)
            longitude.append(lon)
            # Get the altitude the image was taken
            alt = exif["GPS"][piexif.GPSIFD.GPSAltitude][0] / exif["GPS"][piexif.GPSIFD.GPSAltitude][1]
            altitude.append(alt)
            # Get the camera make
            make.append(exif["0th"][piexif.ImageIFD.Make].decode("utf-8"))
            model.append(exif["0th"][piexif.ImageIFD.Model].decode("utf-8"))

        except Exception as e:
            err(str(e))
            failed_indexes.append(i)

    # Remove any failed indexes
    modified_df = sorted_df.drop(failed_indexes)

    modified_df["make"] = make
    modified_df["model"] = model
    modified_df["altitude"] = altitude
    modified_df["latitude"] = latitude
    modified_df["longitude"] = longitude
    modified_df["date"] = date
    modified_df["media_type"] = MediaType.IMAGE
    info(f"Done")
    return modified_df
