# mbari_aidata, Apache-2.0 license
# Filename: commands/load_images.py
# Description: Load images from a directory. Assumes the images are available via a web server.

from pathlib import Path

import click
import requests
from tqdm import tqdm

from mbari_aidata import common_args
from mbari_aidata.commands.load_common import check_mounts, check_duplicate_media
from mbari_aidata.logger import create_logger_file, info, err
from mbari_aidata.plugins.extractors.media_types import MediaType
from mbari_aidata.plugins.loaders.tator.media import gen_spec as gen_media_spec, load_bulk_images
from mbari_aidata.plugins.module_utils import load_module
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
from mbari_aidata.plugins.loaders.tator.common import init_api_project, find_media_type, init_yaml_config


@click.command("images", help="Load images from a directory, a single image file, or a text file with a list of images")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.dry_run
@common_args.duplicates
@click.option("--input", type=str, required=True, help="Path to directory with input images, a single image, or a text file with a list of images")
@click.option("--section", type=str, default="All Media", help="Section to load images into. Default is 'All Media'")
@click.option("--max-images", type=int, default=-1, help="Only load up to max-images. Useful for testing. Default is to load all images")
def load_images(token: str, disable_ssl_verify: bool, config: str, dry_run: bool, input: str, section: str, max_images: int, check_duplicates) -> int:
    """Load images from a directory. Assumes the images are available via a web server. Returns the number of images loaded."""
    create_logger_file("load_images")
    try:
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]
        plugins = config_dict["plugins"]

        # If the input is a text file, arbitrarily choose the first file to check mounts
        if input.endswith(".txt"):
            info(f"Input is a text file. Reading the first line of {input} to check mounts.")
            with open(input, "r") as f:
                first_line = f.readline().strip()
                media, rc = check_mounts(config_dict, first_line, "image")
        else:
            media, rc = check_mounts(config_dict, input, "image")
        if rc == -1:
            return -1

        p = [p for p in plugins if "extractor" in p["name"]][0]  # ruff: noqa
        module = load_module(p["module"])
        extractor = getattr(module, p["function"])

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project, disable_ssl_verify)
        media_type = find_media_type(api, tator_project.id, "Image")

        if not media_type:
            err("Could not find media type Image")
            return -1

        df_media = extractor(Path(input), max_images)
        if len(df_media) == 0:
            info(f"No images found in {input}")
            return 0

        # Keep only the IMAGE media
        df_media = df_media[df_media['media_type'] == MediaType.IMAGE]

        if dry_run:
            info(f"Dry run - not loading {len(df_media)} media")
            return 0

        if check_duplicates:
            duplicates = check_duplicate_media(api, tator_project.id, media_type.id, df_media)
            if len(duplicates) > 0:
                err("Image(s) already loaded")
                info("==== Duplicates ====")
                for d in duplicates:
                    info(d)
                return -1

        specs = []
        num_checked = 0
        for index, row in tqdm(df_media.iterrows(), total=len(df_media), desc="Creating images specs"):
            file_loc_sans_root = row["media_path"].split(media.mount_path.as_posix())[-1]
            image_url = f"{media.base_url}{file_loc_sans_root}"

            if num_checked < 100:
                # Check if the URL is valid, but only for the first 100 images
                info(f"Checking if the url {image_url} is valid")
                try:
                    timeout = 30
                    r = requests.head(image_url, timeout=timeout)
                    if r.status_code != 200:
                        err(f"URL {image_url} is not valid status code {r.status_code}")
                        return -1
                    num_checked += 1
                except Exception as e:
                    err(f"Error checking URL {image_url}: {e}")
                    return -1

            # Check if the image is valid
            if not Path(row["media_path"]).exists():
                err(f"Image {row.media_path} does not exist")
                return -1

            info("Formatting attributes")
            attributes = format_attributes(row.to_dict(), media.attributes)

            specs.append(
                gen_media_spec(
                    file_loc=row.media_path,
                    file_url=image_url,
                    type_id=media_type.id,
                    section=section,
                    attributes=attributes,
                    base_url=media.base_url,
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
