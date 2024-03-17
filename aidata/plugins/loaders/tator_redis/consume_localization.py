# aidata, Apache-2.0 license
# Filename: plugins/loaders/tator_redis/consume_localization.py
# Description: commands related to loading localization data from Redis
import time
import json
import redis

from aidata.plugins.loaders.tator.localization import gen_spec, load_bulk_boxes
from aidata.plugins.attribute_utils import format_attributes
from aidata.logger import info


class ConsumeLocalization:
    def __init__(self, q: redis.Redis, api, tator_project, box_type):
        self.q = q
        self.api = api
        self.tator_project = tator_project
        self.box_type = box_type

    def consume(self):
        while True:
            try:
                info("Waiting for new localizations...")
                keys = self.q.keys("locs:*")
                for k in keys:
                    video_ref = k.decode("utf-8").split(":")[1]
                    load_key = self.q.keys(f"tator_ids:{video_ref}")
                    if len(load_key) == 1:
                        info(f"Loading localization for video ref {video_ref}")
                        hash_data = self.q.hgetall(f"locs:{video_ref}")
                        objects = {key.decode("utf-8"): json.loads(value.decode("utf-8")) for key, value in hash_data.items()}

                        # Load them referencing the video by its load_id
                        info(f"Getting tator_id from {load_key[0]}")
                        tator_id = int(self.q.hget(load_key[0], "tator_id").decode("utf-8"))
                        info(f"Loading {len(objects)} localization(s) for video ref {video_ref} load_id {tator_id}")

                        boxes = []
                        for b in objects:
                            obj = objects[b]
                            import pdb

                            pdb.set_trace()
                            attributes = format_attributes(obj, self.box_type.attributes)
                            version_id = None
                            if "version_id" in obj:
                                version_id = obj["version_id"]
                            boxes.append(
                                gen_spec(
                                    box=[obj["x1"], obj["y1"], obj["x2"], obj["y2"]],
                                    version_id=version_id,
                                    label=obj["label"],
                                    width=obj["width"],
                                    height=obj["height"],
                                    attributes=attributes,
                                    frame_number=obj["frame"],
                                    type_id=self.box_type.id,
                                    media_id=tator_id,
                                    project_id=self.tator_project.id,
                                )
                            )

                        load_bulk_boxes(boxes, self.api, self.tator_project)

                        # Remove them from the queue
                        for obj_id in objects:
                            info(f"Removing localization {obj_id} from queue")
                            self.q.hdel(f"locs:{video_ref}", obj_id)
            except Exception as e:
                info(f"Error: {e}")

            time.sleep(5)
