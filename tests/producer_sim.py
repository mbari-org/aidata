# Test REDIS queue based load for strided video inference workflow for data mining
# Create a Hash to present a video object and a list of localizations for that video
import json
import redis
import requests

from logger import info

idv = 1


def sim_inference(r: redis.Redis, video_url: str, video_ref_uuid: str, iso_start: str):
    """
    Simulate an inference job by creating localizations associated with a video reference
    """
    global idl, idv
    try:
        # Queue the video first
        info(f"video_ref_uuid: {video_ref_uuid}")
        r.hset(f"video_refs_start:{video_ref_uuid}", "start_timestamp", iso_start)
        r.hset(f"video_refs_load:{video_ref_uuid}", "video_uri", video_url)
    except Exception as e:
        info(f"Error: {e}")
        return

    version_id = 0  # Baseline

    # Create localizations
    for i in range(5, 15, 5):
        loc = {
            "x1": 500 + i,
            "y1": 500 + i,
            "x2": 1600 + i,
            "y2": 1000 + i,
            "width": 1920,
            "height": 1080,
            "frame": i,
            "version_id": version_id,
            "score": 0.9,
            "creator": "simulated",
            "cluster": -1,
            "label": "ctenophore",
        }
        r.hset(f"locs:{video_ref_uuid}", str(i), json.dumps(loc))


if __name__ == "__main__":
    # Connect to Redis
    redis_queue = redis.Redis(host="mantis.shore.mbari.org", port=6379, db=1)

    # Clear the database
    redis_queue.flushdb()

    # Simulate inference for a few videos
    for video_name in [
        "V4361_20211006T162656Z_h265_1sec.mp4",
        "V4361_20211006T163256Z_h265_1sec.mp4",
        "D232_20110526T093251.130Z_alt_h264.mp4",
        "D232_20110526T093251.130Z_h264.mp4",
        "V4318_20201208T193416Z_h264.mp4",
        "V4318_20201208T194917Z_h264.mp4",
    ]:
        query = f"http://m3.shore.mbari.org/vam/v1/media/videoreference/filename/{video_name}"
        info(f"query: {query}")
        resp = requests.get(query)
        info(f"resp: {resp}")
        data = json.loads(resp.text)[0]
        video_ref_uuid = data["video_reference_uuid"]
        video_uri = data["uri"]
        start_timestamp = data["start_timestamp"]
        sim_inference(redis_queue, video_uri, video_ref_uuid, start_timestamp)
