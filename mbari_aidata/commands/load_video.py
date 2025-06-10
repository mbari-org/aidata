# mbari_aidata, Apache-2.0 license
# Filename: commands/load_video.py
# Description: Load video into the database
import shutil
from pathlib import Path

import click

from mbari_aidata import common_args
from mbari_aidata.commands.load_common import check_mounts, check_duplicate_media
from mbari_aidata.logger import info, err, create_logger_file
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
from mbari_aidata.plugins.loaders.tator.media import load_media
from mbari_aidata.plugins.module_utils import load_module
from mbari_aidata.plugins.extractors.media_types import MediaType
from mbari_aidata.plugins.loaders.tator.common import init_api_project, find_media_type, init_yaml_config


@click.command("videos", help="Load videos from a directory or a single video")
@common_args.token
@common_args.yaml_config
@common_args.dry_run
@common_args.duplicates
@click.option("--input", type=str, required=True, help="Path to directory with input video or single video")
@click.option("--section", type=str, default="All Media", help="Section to load images into. Default is 'All Media'")
@click.option("--max-videos", type=int, default=-1, help="Only load up to max-videos. Useful for testing. Default is to load all mp4 videos found")
def load_video(token: str, config: str, dry_run: bool, input: str, section: str, max_videos: int, check_duplicates: bool) -> int:
    """Load video(s) from a directory. Returns the number of video loaded."""
    create_logger_file("load_videos")
    # Load the configuration file
    config_dict = init_yaml_config(config)
    project = config_dict["tator"]["project"]
    host = config_dict["tator"]["host"]
    plugins = config_dict["plugins"]

    media, rc = check_mounts(config_dict, input, "video")
    if rc == -1:
        return -1

    api, tator_project = init_api_project(host, token, project)

    media_type = find_media_type(api, tator_project.id, "Video")

    if not media_type:
        err("Could not find media type Videos")
        return -1

    p = [p for p in plugins if "extractor" in p["name"]][0]  # ruff: noqa
    module = load_module(p["module"])
    extractor = getattr(module, p["function"])

    # Check for the needed tools ffmpeg_path, mp4dump_path, and ffprobe_path - this is required to load video
    binaries = ["ffmpeg", "mp4dump", "ffprobe"]
    errors = []
    for binary in binaries:
        try:
            if not shutil.which(binary):
                errors.append(binary)
        except Exception as e:
            err(f"Error checking for {binary}: {e}")

    if len(errors) > 0:
        err(f"The following binaries are missing: {', '.join(errors)}. Please install them or provide the correct path and try again.")
        return -1

    df_media = extractor(media.input_path, max_videos)
    if len(df_media) == 0:
        info(f"No images found in {media.input_path}")
        return 0

    # Keep only the VIDEO media
    df_media = df_media[df_media['media_type'] == MediaType.VIDEO]

    if dry_run:
        info(f'Dry run: Found {len(df_media)} media file to load')
        return len(df_media)

    if check_duplicates:
        duplicates = check_duplicate_media(api, tator_project.id, media_type.id, df_media)
        if len(duplicates) > 0:
            err("Video(s) already loaded")
            info("==== Duplicates ====")
            for d in duplicates:
                info(d)
            return -1

    info(f'Found {len(df_media)} media file to load')
    num_loaded = 0
    for index, row in df_media.iterrows():
        video_path = Path(row['media_path'])
        info(f'Loading {video_path}')
        if not video_path.exists():
            info(f"Video path {video_path} does not exist")
            continue

        # Check if the video is already loaded by its name
        attribute_media_filter = [f"$name::{video_path.name}"]
        medias = api.get_media_list(
            project=tator_project.id,
            type=media_type.id,
            attribute=attribute_media_filter,
        )
        if len(medias) == 1:
            info(f"Video {video_path.name} already loaded")
            continue

        video_url = video_path.as_uri()
        # Remove the file:// prefix and replace the mount path with the base url
        video_url = video_url.replace("file://", "")
        video_url = video_url.replace(media.mount_path.as_posix(), media.base_url)
        iso_datetime = row['iso_start_datetime']

        # Organize by year and month if no section is provided
        if section == "All Media" or len(section) == 0:
            section = f"Video/{iso_datetime.year:02}/{iso_datetime.month:02}"

        attributes = {
            "iso_start_datetime": iso_datetime,
        }
        formatted_attributes = format_attributes(attributes, media.attributes)
        tator_id = load_media(
            media_path=video_path.as_posix(),
            media_url=video_url,
            section=section,
            api=api,
            attributes=formatted_attributes,
            tator_project=tator_project,
            media_type=media_type
        )
        if tator_id:
            num_loaded += 1

    return num_loaded
