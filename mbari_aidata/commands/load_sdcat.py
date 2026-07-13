# mbari_aidata, Apache-2.0 license
# Filename: commands/load_sdcat.py
# Description: Load images referenced in SDCAT formatted CSV files into Tator

from pathlib import Path
import click

from mbari_aidata import common_args


@click.command("sdcat", help="Load images referenced in SDCAT formatted CSV files into Tator")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.dry_run
@common_args.duplicates
@click.option(
    "--input",
    type=Path,
    required=True,
    help="Path to a SDCAT formatted CSV file or a directory containing CSV files",
)
@click.option(
    "--section",
    type=str,
    default="All Media",
    help="Tator section to load images into. Default is 'All Media'",
)
@click.option(
    "--max-images",
    type=int,
    default=-1,
    help="Maximum number of images to load. Default is -1 (load all)",
)
@click.option(
    "--upload",
    is_flag=True,
    help="Upload image files directly to Tator instead of loading by URL reference",
)
def load_sdcat(
    token: str,
    disable_ssl_verify: bool,
    config: str,
    dry_run: bool,
    check_duplicates: bool,
    input: Path,
    section: str,
    max_images: int,
    upload: bool,
) -> int:
    """Load images from an SDCAT formatted CSV file into Tator.

    Reads unique image paths from the ``image_path`` column of the CSV and loads
    them as Image media objects.  With ``--upload`` the files are sent directly to
    Tator; without it the images are registered by URL reference (requires the
    files to be reachable via a configured mount/URL mapping).

    Returns the number of images successfully loaded.
    """
    from mbari_aidata.logger import create_logger_file, info, err
    from mbari_aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
    from mbari_aidata.plugins.loaders.tator.media import (
        gen_spec as gen_media_spec,
        load_bulk_images,
        local_md5_partial,
    )
    from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
    from mbari_aidata.plugins.loaders.tator.common import (
        init_api_project,
        find_media_type,
        init_yaml_config,
    )
    from mbari_aidata.commands.load_common import check_mounts, check_duplicate_media

    create_logger_file("load_sdcat")
    try:
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Extract rows from SDCAT CSV(s)
        df = extract_sdcat_csv(input)
        if df.empty or "image_path" not in df.columns:
            err(f"No image_path entries found in {input}")
            return 0

        # Collect unique image paths and apply optional cap
        image_paths = [Path(p) for p in df["image_path"].unique().tolist()]
        if max_images > 0:
            image_paths = image_paths[:max_images]

        info(f"Found {len(image_paths)} unique image(s) in {input}")

        if dry_run:
            info(f"Dry run: would load {len(image_paths)} image(s)")
            return len(image_paths)

        # Initialise Tator API
        api, tator_project = init_api_project(host, token, project, disable_ssl_verify)
        media_type = find_media_type(api, tator_project.id, "Image")
        if not media_type:
            err("Could not find media type 'Image' in the project")
            return -1

        # Optionally resolve mount → URL mapping (skip when uploading directly)
        media_mount = None
        if not upload:
            first_path = image_paths[0].as_posix()
            media_mount, rc = check_mounts(config_dict, first_path, "image")
            if rc == -1:
                return -1

        # Build per-image attribute dict from config, if present
        image_attributes_cfg = config_dict.get("tator", {}).get("image", {}).get("attributes", {})

        # Duplicate-check against existing Tator media
        if check_duplicates:
            import pandas as pd
            df_paths = pd.DataFrame({"media_path": [p.as_posix() for p in image_paths]})
            duplicates = check_duplicate_media(api, tator_project.id, media_type.id, df_paths)
            if duplicates:
                dup_set = set(duplicates)
                info(f"Skipping {len(dup_set)} already-loaded image(s)")
                image_paths = [p for p in image_paths if p.name not in dup_set]
                if not image_paths:
                    info("All images were duplicates; nothing to load")
                    return 0

        specs = []
        for image_path in image_paths:
            if not image_path.exists():
                err(f"Image not found on disk: {image_path}")
                continue

            attributes = format_attributes({}, image_attributes_cfg) if image_attributes_cfg else {}

            if upload:
                # Direct upload: Tator receives the raw bytes
                spec = gen_media_spec(
                    file_loc=image_path.as_posix(),
                    type_id=media_type.id,
                    section=section,
                    attributes=attributes,
                )
            else:
                # Reference-only: resolve local path to a reachable URL
                file_loc_sans_root = image_path.as_posix().split(
                    media_mount.mount_path.as_posix()
                )[-1]
                image_url = f"{media_mount.base_url}{file_loc_sans_root}"
                spec = gen_media_spec(
                    file_loc=image_path.as_posix(),
                    type_id=media_type.id,
                    section=section,
                    file_url=image_url,
                    attributes=format_attributes({}, media_mount.attributes) if media_mount.attributes else attributes,
                )

            specs.append(spec)

        if not specs:
            info("No valid image specs to load")
            return 0

        info(f"Loading {len(specs)} image(s) into Tator (upload={upload})")
        media_ids = load_bulk_images(tator_project.id, api, specs)
        if media_ids is None:
            err("Error loading images")
            return -1

        info(f"Successfully loaded {len(media_ids)} image(s)")
        return len(media_ids)

    except Exception as e:
        err(f"Error in load_sdcat: {e}")
        raise
