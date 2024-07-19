# aidata, Apache-2.0 license
# Filename: commands/load_boxes.py
# Description: Load images from a directory. Assumes the images are available via a web server.

from pathlib import Path

import click
import requests

from aidata import common_args
from aidata.logger import create_logger_file, info, err
from aidata.plugins.loaders.tator.media import gen_spec as gen_media_spec, load_bulk_images
from aidata.plugins.module_utils import load_module
from aidata.plugins.loaders.tator.attribute_utils import format_attributes
from aidata.plugins.loaders.tator.common import init_api_project, find_media_type, init_yaml_config


@click.command("images", help="Load images from a directory")
@common_args.token
@common_args.yaml_config
@common_args.dry_run
@click.option("--input", type=str, required=True, help="Path to directory with input images")
@click.option("--section", type=str, default="All Media", help="Section to load images into. Default is 'All Media'")
@click.option("--max-images", type=int, help="Only load up to max-images. Useful for testing. Default is to load all images")
def load_images(token: str, config: str, dry_run: bool, input: str, section: str, max_images: int) -> int:
    """Load images from a directory. Assumes the images are available via a web server. Returns the number of images loaded."""
    create_logger_file("load_images")
    try:
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]
        plugins = config_dict["plugins"]
        mounts = config_dict["mounts"]
        image_mount = next((mount for mount in mounts if mount["name"] == "image"), None)

        if not image_mount:
            err("No image mount found in configuration")
            return -1

        if "port" in image_mount:
            port = image_mount["port"]
            image_base_url = f'http://{image_mount["host"]}:{port}'
        else:
            image_base_url = f'http://{image_mount["host"]}'
        if "nginx_root" in image_mount:
            image_base_url = f'{image_base_url}{image_mount["nginx_root"]}/'
        info(f"Image base URL: {image_base_url}")
        image_attributes = config_dict["tator"]["image"]["attributes"]
        image_mount_path = Path(image_mount["path"])
        image_mount_path = image_mount_path.resolve()
        input_path = Path(input)
        input_path = input_path.resolve()

        if not image_mount_path.exists():
            err(f"{image_mount_path} does not exist")
            return -1

        # Check if the image path exists
        if not input_path.exists():
            err(f"{input_path} does not exist")
            return -1

        # Make sure the image_path is a subdirectory of image_mount_path
        if not input_path.is_relative_to(image_mount_path):
            err(f"{input_path} is not a subdirectory of {image_mount_path}")
            return -1

        p = [p for p in plugins if "extractor" in p["name"]][0]  # ruff: noqa
        module = load_module(p["module"])
        extractor = getattr(module, p["function"])

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project)
        media_type = find_media_type(api, tator_project.id, "Image")

        if not input_path.exists():
            err(f"{input_path} does not exist")
            return -1

        df_media = extractor(input_path, max_images)
        if len(df_media) == 0:
            info(f"No images found in {input_path}")
            return 0

        if dry_run:
            info(f"Dry run - not loading {len(df_media)} media")
            return 0

        specs = []
        for index, row in df_media.iterrows():
            file_loc_sans_root = row["image_path"].split(image_mount_path.as_posix())[-1]
            image_url = f"{image_base_url}{file_loc_sans_root}"

            # Check if the URL is valid
            info(f"Checking {image_url}")
            try:
                r = requests.head(image_url)
                if r.status_code != 200:
                    err(f"URL {image_url} is not valid")
                    return -1
            except Exception as e:
                err(f"Error checking URL {image_url}: {e}")
                return -1

            # Check if the image is valid
            if not Path(row["image_path"]).exists():
                err(f"Image {row.image_path} does not exist")
                return -1

            attributes = format_attributes(row.to_dict(), image_attributes)

            specs.append(
                gen_media_spec(
                    file_loc=row.image_path,
                    file_url=image_url,
                    type_id=media_type.id,
                    section=section,
                    attributes=attributes,
                    base_url=image_base_url,
                )
            )
        info(f"Loading {len(specs)} images")
        ids = load_bulk_images(tator_project.id, api, specs)
        if ids is None:
            err(f"Error loading images")
            return -1
        info(f"Loaded {len(ids)} images")
        return len(ids)
    except Exception as e:
        err(f"Error loading images: {e}")
        raise e
