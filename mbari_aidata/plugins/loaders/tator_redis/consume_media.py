# mbari_aidata, Apache-2.0 license
# Filename: loaders/tator_redis/consume_media.py
# Description: commands related to loading media data from Redis
import time
from pathlib import Path
import pytz
from datetime import datetime
import re
import redis

from tator.openapi.tator_openapi import TatorApi  # type: ignore
from tator.openapi.tator_openapi.models import Project, MediaType  # type: ignore
from mbari_aidata.plugins.loaders.tator.media import load_media

from mbari_aidata.logger import info, err
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes


class ConsumeVideo:
    def __init__(
        self,
        r: redis.Redis,
        api: TatorApi,
        tator_project: Project,
        media_type: MediaType,
        mount_path: str,
        ffmpeg_path: str,
        attribute_mapping: dict,
    ):
        self.r = r
        self.api = api
        self.tator_project = tator_project
        self.media_type = media_type
        self.mount_path = mount_path
        self.ffmpeg_path = ffmpeg_path
        self.attribute_mapping = attribute_mapping

    def consume(self):
        while True:
            info("Waiting for new video...")
            try:
                # Get the video references to load
                keys = self.r.keys("video_refs_load:*")
                if len(keys) == 0:
                    info("No video references to load")
                else:
                    for k in keys:
                        video_uri = self.r.hget(k, "video_uri")
                        if video_uri == 'None':
                            err(f"Video uri not found for {k}")
                        else:
                            video_uri = video_uri.decode("utf-8")
                            video_ref = k.decode("utf-8").split(":")[1]

                            if self.r.exists(f"video_refs_start:{video_ref}"):

                                # Check if the video is already loaded by its reference
                                attribute_media_filter = [f"video_reference_uuid::{video_ref}"]
                                medias = self.api.get_media_list(
                                    project=self.tator_project.id,
                                    type=self.media_type.id,
                                    attribute=attribute_media_filter,
                                )
                                if len(medias) == 1:
                                    info(f"Video reference {video_ref} already loaded")
                                    self.r.hset(
                                        f"tator_ids_v:{video_ref}",
                                        "tator_id_v",
                                        str(medias[0].id),
                                    )
                                    continue

                                start_timestamp = self.r.hget(f"video_refs_start:{video_ref}", "start_timestamp").decode("utf-8")
                                pattern_date0 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z")
                                pattern_date1 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z\d*mF*")
                                pattern_date2 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 20161025T184500Z
                                pattern_date3 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z\d*mF*")
                                pattern_date4 = re.compile(r"(\d{2})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 161025T184500Z
                                pattern_date5 = re.compile(r"(\d{2})-(\d{2})-(\d{2})T(\d{2})_(\d{2})_(\d{2})-")
                                pattern_date6 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z") # 2015-03-07T20:53:01.065Z
                                iso_start_datetime = None
                                if pattern_date0.search(start_timestamp):
                                    match = pattern_date0.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date1.search(start_timestamp):
                                    match = pattern_date1.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date2.search(start_timestamp):
                                    match = pattern_date2.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date3.search(start_timestamp):
                                    match = pattern_date3.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date4.search(start_timestamp):
                                    match = pattern_date4.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date5.search(start_timestamp):
                                    match = pattern_date5.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
                                if pattern_date6.search(start_timestamp):
                                    match = pattern_date6.search(start_timestamp).groups()
                                    year, month, day, hour, minute, second, millisecond = map(int, match)
                                    iso_start_datetime = datetime(year, month, day, hour, minute, second, millisecond * 1000, tzinfo=pytz.utc)

                                if iso_start_datetime is None:
                                    info(f"Could not parse start timestamp {start_timestamp}")
                                    continue

                                mount_base = Path(self.mount_path).name
                                video_path = Path(f"{self.mount_path}{video_uri.split(mount_base)[1]}")
                                info(f"Loading video ref {k} uri {video_uri}")
                                if not video_path.exists():
                                    info(f"Video path {video_path} does not exist")
                                else:
                                    # Organize by year and month
                                    section = f"Video/{iso_start_datetime.year:02}/{iso_start_datetime.month:02}"

                                    # TODO: add support for different payloads
                                    attributes = {
                                        "iso_start_datetime": iso_start_datetime,
                                        "video_reference_uuid": video_ref,
                                    }
                                    formatted_attributes = format_attributes(attributes, self.attribute_mapping)
                                    tator_id = load_media(
                                        ffmpeg_path=self.ffmpeg_path,
                                        media_path=video_path.as_posix(),
                                        media_url=video_uri,
                                        section=section,
                                        api=self.api,
                                        attributes=formatted_attributes,
                                        tator_project=self.tator_project,
                                        media_type=self.media_type,
                                    )
                                    self.r.hset(f"tator_ids_v:{video_ref}", "tator_id_v", str(tator_id))

            except Exception as e:
                err(f"Error consuming video {e}")
                time.sleep(60)

            time.sleep(60)
