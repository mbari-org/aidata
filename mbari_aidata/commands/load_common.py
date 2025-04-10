# mbari_aidata, Apache-2.0 license
# Filename: commands/load_common.py
# Description: Common functions for loading different media, e.g. images or video from a directory mapped to a web server
from pathlib import Path
from typing import Dict, List

import pandas as pd
from tator.openapi.tator_openapi import TatorApi

from mbari_aidata.logger import info, err

class MediaHelper:
    input_path: Path
    mount_path: Path
    base_url: str
    attributes: dict

def check_duplicate_media(api: TatorApi, project_id:int, media_type:int, df_media: pd.DataFrame) -> List[str]:
    """Check if the images are already loaded to avoid duplicates"""
    media_names = []
    for index, row in df_media.iterrows():
        name = Path(row["media_path"]).name
        media = api.get_media_list(project_id, name=name, type=media_type)
        if media:
            media_names.append(name)
    return media_names

def check_mounts(config_dict: Dict, input:str, media_type: str) -> (MediaHelper, int):
    mounts = config_dict["mounts"]
    media_mount = next((mount for mount in mounts if mount["name"] == media_type), None)

    if not media_mount:
        err("No image mount found in configuration")
        return None, -1

    if 'http' in media_mount["host"]:
        base_url = media_mount["host"]
    else:
        base_url = f'http://{media_mount["host"]}' # assuming http protocol which may not be correct

    if "port" in media_mount:
        port = media_mount["port"]
        base_url = f'{base_url}:{port}'

    if "nginx_root" in media_mount:
        base_url = f'{base_url}{media_mount["nginx_root"]}/'
    info(f"Media base URL: {base_url}")
    attributes = config_dict["tator"][media_type]["attributes"]
    mount_path = Path(media_mount["path"])
    mount_path = mount_path.resolve()
    input_path = Path(input)
    input_path = input_path.resolve()

    if not input_path.exists():
        err(f"{input_path} does not exist")
        return None, -1

    media = MediaHelper()
    media.input_path = input_path
    media.mount_path = mount_path
    media.base_url = base_url
    media.attributes = attributes

    if not mount_path.exists():
        err(f"{mount_path} does not exist")
        return None, -1

    # Check if the image path exists
    if not input_path.exists():
        err(f"{input_path} does not exist")
        return None, -1

    # If the input path is a directory, check if it is a subdirectory of the media mount path
    if input_path.is_dir():
        dir_or_file = input_path
    else:
        dir_or_file = input_path.parent

    if not dir_or_file.is_relative_to(mount_path):
        err(f"{dir_or_file} is not a subdirectory of the mount path {mount_path}. "
            f"This is required to load the media correctly.")
        return None, -1

    return media, 0