# mbari_aidata, Apache-2.0 license
# Filename: commands/load_common.py
# Description: Common functions for loading different media, e.g. images or video from a directory
from pathlib import Path
from typing import Dict

from mbari_aidata.logger import info, err

class MediaHelper:
    input_path: Path
    mount_path: Path
    base_url: str
    attributes: dict

def check_mounts(config_dict: Dict, input:str, media_type: str) -> (MediaHelper, int):
    mounts = config_dict["mounts"]
    media_mount = next((mount for mount in mounts if mount["name"] == media_type), None)

    if not media_mount:
        err("No image mount found in configuration")
        return None, -1

    if "port" in media_mount:
        port = media_mount["port"]
        base_url = f'http://{media_mount["host"]}:{port}'
    else:
        base_url = f'http://{media_mount["host"]}'
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
        err(f"{dir_or_file} is not a subdirectory of {mount_path}")
        return None, -1

    return media, 0