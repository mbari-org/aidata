# mbari_aidata, Apache-2.0 license
# Filename: loaders/tator_redis/consume_media.py
# Description: commands related to loading media data from Redis
import time
from pathlib import Path
import pytz
from datetime import datetime
from dateutil.parser import isoparse
import re
import redis
from tator.openapi.tator_openapi import TatorApi  # type: ignore
from tator.openapi.tator_openapi.models import Project, MediaType  # type: ignore

from mbari_aidata.plugins.loaders.tator.media import load_media
from mbari_aidata.logger import info, err, debug
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
        mount_base = Path(self.mount_path).name
        while True:
            info("Waiting for new video...")
            try:
                video_refs = []
                # Get the video references to load
                for key in self.r.scan_iter("video_refs_load:*"):
                    data = self.r.hgetall(key)
                    decoded = {k.decode("utf-8"): v.decode("utf-8") for k, v in data.items()}
                    video_refs.append(decoded)
                    debug(f"Found video refs {decoded}")

                for ref in video_refs:
                    video_uri = ref["video_uri"]
                    video_uuid = ref["video_ref_uuid"]

                    if not self.r.exists(f"video_refs_start:{video_uri}"):
                        info(f'No data: video_refs_start emtpy for {video_uri}')
                        continue

                    if 'i2MAP' in video_uri:
                        uri = video_uri.replace('/M3/master/', '/DeepSea-AI/data/')
                        uri = uri.replace('.mov', '.mp4')
                    else:
                        uri = video_uri

                    info(f"{uri} {self.mount_path} {mount_base}")
                    video_path = Path(f"{self.mount_path}{uri.split(mount_base)[-1]}")

                    if not video_path.exists():
                        err(f"Video path {video_path} does not exist")
                        exit(-1)

                    # Check if the video is already loaded by its name
                    info(f"Checking if video {video_path.name} is already loaded")
                    medias = self.api.get_media_list(self.tator_project.id, name=video_path.name, type=self.media_type.id)
                    if len(medias) >= 1:
                        info(f"Video {video_uri} already loaded to {medias[0].id}")
                        self.r.hset(f"tator_ids_v:{video_uri}", "tator_id_v", medias[0].id)
                        continue

                    start_timestamp = self.r.hget(f"video_refs_start:{video_uri}", "start_timestamp").decode("utf-8")
                    pattern_date0 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z")
                    pattern_date1 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z\d*mF*")
                    pattern_date2 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 20161025T184500Z
                    pattern_date3 = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z\d*mF*")
                    pattern_date4 = re.compile(r"(\d{2})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z")  # 161025T184500Z
                    pattern_date5 = re.compile(r"(\d{2})-(\d{2})-(\d{2})T(\d{2})_(\d{2})_(\d{2})-")
                    pattern_date6 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z") # 2015-03-07T20:53:01.065Z
                    pattern_date7 = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{6})") # 2025-04-25T04:11:23.770409
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
                    if pattern_date7.search(start_timestamp):
                        match = pattern_date7.search(start_timestamp).groups()
                        year, month, day, hour, minute, second, microsecond = map(int, match)
                        iso_start_datetime = datetime(year, month, day, hour, minute, second, microsecond, tzinfo=pytz.utc)

                    if iso_start_datetime is None:
                        iso_start_datetime = isoparse(start_timestamp)
                        if iso_start_datetime.tzinfo is None:
                            err(f"Could not parse start timestamp {start_timestamp}")
                            exit(-1)
                    if iso_start_datetime is None:
                        err(f"Could not parse start timestamp {start_timestamp}")
                        exit(-1)

                    # Organize by year and month
                    section = f"Video/{iso_start_datetime.year:02}/{iso_start_datetime.month:02}"

                    # TODO: add support for different payloads
                    attributes = {
                        "iso_start_datetime": iso_start_datetime,
                        "video_reference_uuid": video_uuid,
                    }
                    formatted_attributes = format_attributes(attributes, self.attribute_mapping)
                    tator_id = load_media(
                        ffmpeg_path=self.ffmpeg_path,
                        media_path=video_path.as_posix(),
                        media_url=uri,
                        section=section,
                        api=self.api,
                        attributes=formatted_attributes,
                        tator_project=self.tator_project,
                        media_type=self.media_type,
                    )
                    self.r.hset(f"tator_ids_v:{video_uri}", "tator_id_v", str(tator_id))

            except Exception as e:
                err(f"Error consuming video {e}")
                exit(-1)

            time.sleep(30)
