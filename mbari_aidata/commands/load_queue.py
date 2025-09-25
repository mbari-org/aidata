# mbari_aidata, Apache-2.0 license
# Filename: commands/load_queue.py
# Description: Commands for loading data from a Redis message queue

import concurrent
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path

import click
import os
import redis
from mbari_aidata import common_args
from mbari_aidata.logger import info, create_logger_file
from mbari_aidata.plugins.loaders.tator_redis.consume_localization import ConsumeLocalization
from mbari_aidata.plugins.loaders.tator_redis.consume_media import ConsumeVideo
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, init_api_project, find_media_type, find_box_type


@click.command("queue", help="Load data from a Redis message queue")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@click.option("--reset", is_flag=True, help="Reset the Redis queue. CAUTION: This will delete all data in the queue.")
def load_queue(token: str, disable_ssl_verify: bool, config: str, reset: bool) -> None:
    """Load data from a Redis message queue."""
    create_logger_file("load_queue")

    # Load the configuration file
    config_dict = init_yaml_config(config)
    project = config_dict["tator"]["project"]
    host = config_dict["tator"]["host"]
    video_attributes = config_dict["tator"]["video"]["attributes"]

    # Connect to Redis
    redis_host = config_dict["redis"]["host"]
    redis_port = config_dict["redis"]["port"]
    r = redis.Redis(host=redis_host, port=redis_port, password=os.getenv("REDIS_PASSWORD"))

    if reset:
        # Reset the Redis queue
        info("Resetting the Redis queue")
        r.flushdb()
        info("Redis queue reset")

    # Initialize the Tator API
    api, tator_project = init_api_project(host, token, project, disable_ssl_verify)
    media_type_v = find_media_type(api, tator_project.id, "Video")
    box_type = find_box_type(api, tator_project.id, "Box")
    if box_type is None:
        info(f"No box type found in project {project}")
        return
    if media_type_v is None:
        info(f"No media type found in project {project}")
        return

    # Get the mount path from the configuration
    mounts = config_dict["mounts"]
    mount_path = None
    mount_host = None
    mount_nginx = None
    for mount in mounts:
        if mount["name"] == "video":
            mount_path = mount["path"]
            mount_host = mount["host"]
            mount_nginx = mount["nginx_root"]
    if mount_path is None:
        info("Mount path not found")
        return

    # Get the ffmpeg path from the configuration
    ffmpeg_path = config_dict["ffmpeg_path"]
    if not Path(ffmpeg_path).exists():
        info(f"FFMPEG path {ffmpeg_path} does not exist. Correct the configuration file {config}.")
        return

    # Create consumers
    consumers = [
        ConsumeVideo(
            r,
            api,
            tator_project,
            media_type_v,
            mount_nginx,
            mount_path,
            mount_host,
            ffmpeg_path,
            video_attributes,
        ),
        ConsumeLocalization(r, api, tator_project, box_type),
    ]

    # Cache video reference to tator id in Redis
    # This is used to avoid querying Tator for the same video reference
    medias = api.get_media_list(project=tator_project.id, type=media_type_v.id)
    for media in medias:
        # TODO: check if video_reference_uuid is in attributes
        video_ref = media.attributes["video_reference_uuid"]
        r.hset(f"tator_ids_v:{video_ref}", "tator_id_v", str(media.id))

    # Image type found in Tator
    # TODO: add support for image ingest

    executor = ThreadPoolExecutor(max_workers=len(consumers))
    futures = [executor.submit(consumer.consume) for consumer in consumers]
    [future.result() for future in concurrent.futures.as_completed(futures)]
