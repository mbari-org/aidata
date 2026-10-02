# mbari_aidata, Apache-2.0 license
# Filename: commands/load_images.py
# Description: Load images from a directory. Assumes the images are available via a web server.

from pathlib import Path
from typing import Optional, Union

import click

from mbari_aidata import common_args


def reference_url_accepted(status_code: int) -> bool:
    """A reference image URL is usable only when it responds 200.

    Redirects such as 301 are rejected so a bad URL stops the load.
    """
    return status_code == 200


def resolve_media_path(media_path: str, base_path: Optional[Path]) -> str:
    """Prefix a relative media path with base_path. Absolute and http paths are unchanged."""
    path = str(media_path)
    if base_path is None or path.startswith("http") or Path(path).is_absolute():
        return path
    return str(base_path / path)


def reference_image_url(media_path: str, base_url: str, url_root: Union[str, Path]) -> str:
    """Build a reference image URL by stripping url_root from a local media path.

    Paths that already start with http are returned unchanged.
    """
    if str(media_path).startswith("http"):
        return str(media_path)

    root = Path(url_root).as_posix().rstrip("/")
    candidates = [str(media_path)]
    resolved = Path(media_path).resolve().as_posix()
    if resolved not in candidates:
        candidates.append(resolved)

    for candidate in candidates:
        if candidate == root or candidate.startswith(root + "/"):
            relative = candidate[len(root):].lstrip("/")
            return f"{base_url.rstrip('/')}/{relative}" if relative else base_url.rstrip("/")

    raise ValueError(f"{media_path} is not under base path {url_root}")


@click.command("images", help="Load images from a directory, a single image file, a text listing of images, or the image_path column from a SDCAT formatted CSV")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.dry_run
@common_args.duplicates
@click.option("--input", type=str, required=True, help="Path to directory with input images, a single image, a text file with a list of images, or a SDCAT formatted CSV")
@click.option("--section", type=str, default="All Media", help="Section to load images into. Default is 'All Media'")
@click.option("--max-images", type=int, default=-1, help="Only load up to max-images. Useful for testing. Default is to load all images")
@click.option("--upload", is_flag=True, help="Upload image files directly instead of loading by reference")
@click.option(
    "--base-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Directory joined to relative image filenames to locate the files. The hosted URL still strips the config mount path. Only valid when --upload is not used.",
)
def load_images(token: str, disable_ssl_verify: bool, config: str, dry_run: bool, input: str, section: str, max_images: int, check_duplicates: bool, upload: bool, base_path: Optional[Path]) -> int:
    """Load images from a directory. Returns the number of images loaded."""
    import inspect
    import requests
    from tqdm import tqdm

    if base_path is not None and upload:
        raise click.UsageError("--base-path is only valid when --upload is not used")

    from mbari_aidata.commands.load_common import check_mounts, exclude_loaded_media, get_media_attributes
    from mbari_aidata.logger import create_logger_file, info, err
    from mbari_aidata.plugins.extractors.media_types import MediaType
    from mbari_aidata.plugins.loaders.tator.media import (
        MEDIA_CREATE_BATCH,
        SpecBatcher,
        gen_spec as gen_media_spec,
        load_bulk_images,
        upload_image,
    )
    from mbari_aidata.plugins.module_utils import load_module
    from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
    from mbari_aidata.plugins.loaders.tator.common import init_api_project, find_media_type, init_yaml_config

    create_logger_file("load_images")
    try:
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]
        plugins = config_dict["plugins"]

        # Skip mount check when uploading directly
        if upload:
            media = None
        else:
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

        extractor_kwargs = {}
        if dry_run and "parse_timestamps" in inspect.signature(extractor).parameters:
            extractor_kwargs["parse_timestamps"] = False
        df_media = extractor(Path(input), max_images, **extractor_kwargs)
        if base_path is not None and len(df_media) > 0 and "media_path" in df_media.columns:
            df_media = df_media.copy()
            df_media["media_path"] = df_media["media_path"].map(lambda p: resolve_media_path(p, base_path))
        if len(df_media) == 0:
            info(f"No images found in {input}")
            return 0

        # Keep only the IMAGE media
        df_media = df_media[df_media['media_type'] == MediaType.IMAGE]

        if dry_run:
            info(f"Dry run - not loading {len(df_media)} media")
            return 0

        # A later run skips filenames already stored and loads only the remainder.
        if check_duplicates:
            info("Duplicate check requested; image loads always skip media already in the project")
        df_media = exclude_loaded_media(api, tator_project.id, media_type.id, df_media)
        if len(df_media) == 0:
            info("All images were already loaded; nothing to load")
            return 0

        if upload:
            # Fetch attribute mapping from Tator so metadata (depth, iso_datetime, …) is forwarded
            image_attributes = get_media_attributes(config_dict, "image", api=api, project_id=tator_project.id)

            # Direct upload path: transfer bytes to Tator so transcoding is triggered
            num_loaded = 0
            for index, row in tqdm(df_media.iterrows(), total=len(df_media), desc="Uploading images"):
                if not Path(row["media_path"]).exists():
                    err(f"Image {row.media_path} does not exist")
                    continue
                attributes = format_attributes(row.to_dict(), image_attributes)
                media_id = upload_image(
                    image_path=row.media_path,
                    attributes=attributes,
                    api=api,
                    tator_project=tator_project,
                    media_type=media_type,
                    section=section,
                )
                if media_id is not None:
                    num_loaded += 1
            info(f"Uploaded {num_loaded} images")
            return num_loaded

        # Reference-only path: build URL specs and create them in batches so a
        # load of millions of images does not hold every spec before the first create.
        def create_specs(specs):
            return load_bulk_images(tator_project.id, api, specs)

        batcher = SpecBatcher(create_specs, batch_size=MEDIA_CREATE_BATCH)
        num_checked = 0
        # Materialize one create-batch of rows at a time so a multi-million
        # frame is not copied into a second full list of dicts.
        row_batches = (
            df_media.iloc[start:start + MEDIA_CREATE_BATCH].to_dict("records")
            for start in range(0, len(df_media), MEDIA_CREATE_BATCH)
        )
        rows = (row for batch in row_batches for row in batch)
        for row in tqdm(rows, total=len(df_media), desc="Creating image specs"):
            try:
                image_url = reference_image_url(row["media_path"], media.base_url, media.mount_path)
            except ValueError as e:
                err(str(e))
                return -1

            if num_checked < 100:
                # Check if the URL is valid, but only for the first 100 images
                info(f"Checking if the url {image_url} is valid")
                try:
                    timeout = 30
                    r = requests.head(image_url, timeout=timeout)
                    if reference_url_accepted(r.status_code):
                        info(f"URL {image_url} is valid code {r.status_code}")
                        num_checked += 1
                    else:
                        err(f"URL {image_url} is not valid status code {r.status_code}")
                        return -1
                except Exception as e:
                    err(f"Error checking URL {image_url}: {e}")
                    return -1

            if not str(row["media_path"]).startswith("http"):
                if not Path(row["media_path"]).exists():
                    err(f"Image {row.media_path} does not exist")
                    return -1

            attributes = format_attributes(row, media.attributes)

            spec = gen_media_spec(
                file_loc=row["media_path"],
                file_url=image_url,
                type_id=media_type.id,
                section=section,
                attributes=attributes,
                base_url=media.base_url,
            )
            if not batcher.add(spec):
                err("Error loading images")
                return -1

        if not batcher.flush():
            err("Error loading images")
            return -1
        info(f"Loaded {len(batcher.ids)} images")
        return len(batcher.ids)
    except Exception as e:
        err(f"Error loading images: {e}")
        raise e
