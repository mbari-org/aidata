# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator_redis/consume_localization.py
# Description: commands related to loading localization data from Redis
import time
import json
import redis

from mbari_aidata.plugins.loaders.tator.localization import gen_spec, load_bulk_boxes
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
from mbari_aidata.logger import info, debug, err


class ConsumeLocalization:
    def __init__(self, r: redis.Redis, api, tator_project, box_type):
        self.r = r
        self.api = api
        self.tator_project = tator_project
        self.box_type = box_type
        # Create a dictionary of key/values from the box type attributes field name and dtype
        self.attribute_mapping = {a.name: {"type": a.dtype} for a in box_type.attribute_types}

    def consume(self):
        while True:
            info("Waiting for new localizations...")
            try:
                for video_uri in self.r.scan_iter("locs:*"):
                    data = self.r.hgetall(video_uri)
                    video_uri = video_uri.decode("utf-8").split("locs:")[-1]
                    info(f"video_uri {video_uri}")
                    if data is None:
                        continue

                    info(f"Found localization {video_uri} total locs {len(data)}")
                    loc_items = {k.decode("utf-8"): v.decode("utf-8") for k, v in data.items()}
                    info(f"Found localization {video_uri} total locs {len(loc_items)}")

                    if not self.r.exists(f"tator_ids_v:{video_uri}"):
                        info(f'No data: tator_ids_v empty for {video_uri}')
                        continue

                    tator_id_v = self.r.hget(f"tator_ids_v:{video_uri}", "tator_id_v")
                    if tator_id_v is not None:
                        tator_id = tator_id_v.decode("utf-8")
                        info(f"Found tator id {tator_id} for {video_uri}")
                    else:
                        info(f'No data: tator_ids_v empty for {video_uri}')
                        continue

                    seen_boxes = set()
                    boxes = []
                    l_ids = []

                    for l_id, l in loc_items.items():
                        l_id = int(l_id)
                        l_ids.append(l_id)
                        info(f"Found localization {l_id} for {video_uri}\n")
                        l = json.loads(l)
                        info(f"Formatting attributes in {l}")
                        attributes = format_attributes(l, self.attribute_mapping)
                        label = l.get('label') or l.get('Label')
                        # Define uniqueness based only on box coordinates and frame number
                        box_key = ( l["x1"], l["y1"], l["x2"], l["y2"], l["frame"])
                        if box_key in seen_boxes:
                            info(f"Duplicate box found for {box_key}, skipping.")
                            continue 
                        seen_boxes.add(box_key)
                        box = gen_spec(
                                box=[l["x1"], l["y1"], l["x2"], l["y2"]],
                                version_id=l["version_id"],
                                label=label,
                                width=l["width"],
                                height=l["height"],
                                attributes=attributes,
                                frame_number=l["frame"],
                                type_id=self.box_type.id,
                                media_id=int(tator_id),
                                project_id=self.tator_project.id,
                            )
                        boxes.append(box)

                    load_bulk_boxes(self.tator_project.id, self.api, boxes)

                    # Remove them from the queue
                    for l_id in l_ids:
                        info(f"Removing localization {l_id} from queue")
                        self.r.hdel(f"locs:{video_uri}", l_id)
            except Exception as e:
                info(f"Error: {e}")
                time.sleep(5)

            time.sleep(5)
