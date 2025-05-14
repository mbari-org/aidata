# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/media.py
# Description:  Database operations related to media
import hashlib
import os
from tempfile import TemporaryDirectory
from typing import List, Any, Dict

from moviepy import VideoFileClip
import mimetypes
import subprocess

from pathlib import Path
from uuid import uuid1
import tator  # type: ignore
from tator.openapi.tator_openapi import TatorApi as tatorapi, Project, MediaType  # type: ignore
from PIL import Image
from tator.util._upload_file import _upload_file  # type: ignore
from tator.openapi.tator_openapi import MessageResponse  # type: ignore
from mbari_aidata.logger import err, debug, info
from mbari_aidata.plugins.loaders.tator.common import find_media_type, init_api_project


def get_media_ids(
        api: tator.api,
        project: Project,
        image_type: int,
        **kwargs
        ) -> Dict[str, int]:
        """
        `Get the media ids that match the filter
        :param api:  tator api
        :param kwargs:  filter arguments to pass to the get_media_list function
        :return: media name to id mapping
        """
        media_map = {}
        media_count = api.get_media_count(project=project.id, type=image_type, **kwargs)
        if media_count == 0:
            err(f"No media found in project {project.name}")
            return media_map
        batch_size = min(1000, media_count)
        debug(f"Searching through {media_count} medias with {kwargs}")
        for i in range(0, media_count, batch_size):
            media = api.get_media_list(project=project.id, start=i, stop=i + batch_size, **kwargs)
            info(f"Found {len(media)} medias with {kwargs} {i} {i + batch_size}")
            for m in media:
                media_map[m.name] = m.id
                debug(f"Found {len(media_map)} medias with {kwargs}")
        return media_map


def local_md5_partial(file_name, max_chunks=5):
    """Computes md5sum-based fingerprint of the first part of a local file.
    Faster than computing the full md5sum and best done on the client side.

    :param file_name: Path to the local file.
    :param max_chunks: Maximum number of chunks to download.
    :returns: md5 sum of the first part of the file.
    """
    CHUNK_SIZE = 2 * 1024 * 1024
    chunk_count = 0
    md5 = hashlib.md5()

    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            if chunk:
                chunk_count += 1
                md5.update(chunk)
            if chunk_count >= max_chunks:
                break

    return md5.hexdigest()


def gen_spec(file_loc: str, type_id: int, section: str, **kwargs) -> dict:
    """
    Generate a media spec for Tator
    :param file_loc: file location
    :param type_id: media type ID
    :param section: section to assign to the media - this corresponds to a Tator section which is a collection, akin to a folder.
    :return: The media spec
    """
    file_load_path = Path(file_loc)
    attributes = kwargs.get("attributes")
    file_url = kwargs.get("file_url")  # The URL to the file if hosted.

    if file_url:
        debug(f"spec URL: {file_url}")
        spec = {
            "type": type_id,
            "url": file_url,
            "name": file_load_path.name,
            "section": section,
            "md5": local_md5_partial(file_load_path),
            "size": file_load_path.stat().st_size,
            "attributes": attributes,
            "gid": str(uuid1()),
            "uid": str(uuid1()),
            "reference_only": 1,
        }
    else:
        debug(f"spec file path: {file_loc}")
        spec = {
            "name": file_load_path.name,
            "type": type_id,
            "path": file_loc,
            "section": section,
            "md5": local_md5_partial(file_loc),
            "size": file_load_path.stat().st_size,
            "attributes": attributes,
            "gid": str(uuid1()),
            "uid": str(uuid1()),
            "reference_only": 0,
        }

    if attributes:
        spec["attributes"] = attributes

    return spec

def gen_thumbnail_jpg(ffmpeg_path: str, video_path: str, thumb_jpg_path: str):
    # Create jpg thumbnail in a single pass
    cmd = [
        ffmpeg_path,
        "-y",
        "-i",
        f'{video_path}',
        "-vf",
        f"select=eq(n\,0),scale=256:-1:flags=lanczos",
        "-frames:v",
        "1",
        thumb_jpg_path,
    ]
    info(f"cmd={cmd}")
    debug(' '.join(cmd))
    subprocess.run(cmd, check=True)

def gen_thumbnail_gif(ffmpeg_path: str, num_frames: int, fps: float, video_path: str, thumb_gif_path: str):
    # Create gif thumbnail in a single pass
    # This logic makes a max 10 second summary video and saves as a gif
    video_duration = int(num_frames / fps)

    # Max thumbnail duration is 10 seconds
    thumb_duration = min(10, video_duration)

    # If the video duration is shorter than the thumb duration, adjust the gif to be the video duration
    if video_duration < 10:
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            f'{video_path}',
            "-vf",
            f"fps={int(fps)},scale=256:-1:flags=lanczos",
            "-an",
            thumb_gif_path,
        ]
    else:
        frame_select = max(fps, (video_duration / thumb_duration) * fps)
        speed_up = 64 * max(1, round(video_duration / thumb_duration))

        debug(f"Creating {thumb_gif_path} frame_select={frame_select} speed_up={speed_up}")
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            f'{video_path}',
            "-vf",
            f"select='not(mod(n,{round(frame_select)}))',scale=256:-1:flags=lanczos,setpts=PTS/{speed_up},fps=24",
            "-an",
            thumb_gif_path,
        ]
    info(f"cmd={cmd}")
    debug(' '.join(cmd))
    subprocess.run(cmd, check=True)


def get_video_metadata(video_url_or_path: Path) -> dict or None:
    try:
        video_clip = VideoFileClip(video_url_or_path.as_posix())
        reader_metadata = video_clip.reader.infos.get('metadata')
        if '.mp4' in video_url_or_path.suffix.lower():
            fallback_codec = 'h264'
        else:
            fallback_codec = 'unknown'
        metadata = {
            "codec": reader_metadata.get("encoder", fallback_codec),
            "mime": mimetypes.guess_type(video_url_or_path.as_posix())[0],
            "resolution": video_clip.reader.size,
            "size": os.stat(video_url_or_path).st_size,
            "num_frames": video_clip.reader.n_frames,
            "frame_rate": video_clip.reader.fps,
            "bit_rate": video_clip.reader.bitrate*1e3,
        }
        video_clip.close()
        return metadata
    except Exception as e:
        print("Error:", e)
        return None


def load_bulk_images(project_id: int, api: tatorapi, specs: list) -> List[int]:
    """
    Load a list of media objects to the database.
    :param project_id: The project ID
    :param api: The Tator API object.
    :param specs: List of image media specs created
    :return: List of media IDs
    """
    try:
        chunk_size = min(500, len(specs))
        media_ids = []
        info(f"Creating {len(specs)} media images")
        media_ids += [
            new_id
            for response in tator.util.chunked_create(api.create_media_list, project_id, chunk_size=chunk_size, body=specs)
            for new_id in response.id
        ]
        info(f"Created {len(media_ids)} medias")
        return media_ids
    except Exception as e:
        err(f"Error creating media images {e}")
        return []


def load(ffmpeg_path: str, project_id: int, api: tatorapi, media_path: str, spec: Dict, **kwargs: Any) -> int or None:
    """
    Load image/video reference to the database. This creates a media object,
    and a thumbnail gif representation of the video.
    :param ffmpeg_path: Path to the ffmpeg binary
    :param project_id: The project ID
    :param api: The Tator API object.
    :param media_path: The media path to load
    :param spec: The media spec to create
    :param kwargs: Additional arguments
    :return: The media ID or None if failed
    """
    media_id = None
    try:
        metadata = None
        is_video = False
        # if the media is a video, create a thumbnail gif
        possible_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        video_path = Path(media_path)
        if video_path.suffix.lower() in possible_extensions:
            is_video = True

        if is_video:
            metadata = get_video_metadata(video_path)
            if not metadata:
                raise Exception(f"Error getting metadata for {media_path}")
            media_spec = {
                "type": spec["type"],
                "section": spec["section"],
                "name": spec["name"],
                "md5": spec["md5"],
                "attributes": spec["attributes"],
                "width": metadata["resolution"][0],
                "height": metadata["resolution"][1],
                "num_frames": metadata["num_frames"],
                "fps": metadata["frame_rate"],
                "bit_rate": metadata["bit_rate"],
                "codec": metadata["codec"],
                "mime": metadata["mime"],
            }
        else:
            media_spec = {
                "type": spec["type"],
                "section": spec["section"],
                "name": spec["name"],
                "md5": spec["md5"],
                "url": spec["url"],
                "attributes": spec["attributes"],
                "width": kwargs["image_width"] if "image_width" in kwargs else 1920,
                "height": kwargs["image_height"] if "image_height" in kwargs else 1080,
            }

        response = api.create_media_list(project_id, [media_spec])
        media_id = response.id[0]

        if metadata is None:
            raise Exception(f"Error getting metadata for {media_id}")

        with TemporaryDirectory() as tmpdir:
            name = Path(spec["name"])
            thumb_path = f"/tmp/{name.stem}_thumbnail.jpg"
            thumb_gif_path = f"/{tmpdir}/{name.stem}_thumbnail_gif.gif"
            gen_thumbnail_gif(
                ffmpeg_path,
                metadata["num_frames"],
                metadata["frame_rate"],
                media_path,
                thumb_gif_path,
            )
            gen_thumbnail_jpg(
                ffmpeg_path,
                media_path,
                thumb_path,
            )
            # Check if the thumbnail gif was created and is not empty
            if not os.path.exists(thumb_gif_path) or os.stat(thumb_gif_path).st_size == 0:
                raise Exception(f"Thumbnail gif {thumb_gif_path} not created or empty")

            for progress, thumbnail_info in _upload_file(
                api,
                project_id,
                thumb_path,
                media_id=media_id,
                filename=os.path.basename(thumb_path),
            ):
                info(f"Thumbnail {thumb_path} upload progress: {progress}%")
                pass

            for progress, thumbnail_gif_info in _upload_file(api, project_id, media_id=media_id, path=thumb_gif_path, filename=os.path.basename(thumb_gif_path), timeout=30):
                pass

            info(f"Thumbnail {thumb_gif_path} upload progress: {progress}%")

            for progress, thumbnail_gif_info in _upload_file(
                api,
                project_id,
                thumb_gif_path,
                media_id=media_id,
                filename=os.path.basename(thumb_gif_path),
            ):
                info(f"Thumbnail {thumb_gif_path} upload progress: {progress}%")

            thumb_gif_image = Image.open(thumb_gif_path)
            thumb_gif_def = {
                "path": thumbnail_gif_info.key,
                "size": os.stat(thumb_gif_path).st_size,
                "resolution": [thumb_gif_image.height, thumb_gif_image.width],
                "mime": f"image/{thumb_gif_image.format.lower()}"
            }
            thumb_image = Image.open(thumb_path)
            thumb_def = {
                "path": thumbnail_info.key,
                "size": os.stat(thumb_path).st_size,
                "resolution": [thumb_image.height, thumb_image.width],
                "mime": f"image/{thumb_image.format.lower()}"
            }
            response = api.create_image_file(media_id, role="thumbnail_gif", image_definition=thumb_gif_def)
            if not isinstance(response, MessageResponse):
                raise Exception(f"Creating thumbnail gif {thumb_gif_path}")
            response = api.create_image_file(media_id, role="thumbnail", image_definition=thumb_def)
            if not isinstance(response, MessageResponse):
                raise Exception(f"Creating thumbnail {thumb_path}")

            # # Update the media object.
            response = api.update_media(
                media_id,
                media_update={
                    "num_frames": metadata["num_frames"],
                    "fps": metadata["frame_rate"],
                    "codec": metadata["codec"],
                    "width": metadata["resolution"][0],
                    "height": metadata["resolution"][1],
                },
            )
            if not isinstance(response, MessageResponse):
                raise Exception(f"Updating media {media_id}")

            video_def = {
                "codec": metadata["codec"],
                "codec_description": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                "size": metadata["size"],
                "bit_rate": metadata["bit_rate"],
                "resolution": [metadata["resolution"][1], metadata["resolution"][0]],
                "path": spec["url"],
                "reference_only": 1,
            }
            api.create_video_file(media_id, role="streaming", video_definition=video_def)
        return media_id
    except Exception as e:
        err(f"Error creating media {media_path} {e}")
        if media_id:
            # Remove the media object
            api.delete_media(media_id)
        return None


def load_media(
    ffmpeg_path: str,
    media_path: str,
    media_url: str,
    attributes: dict,
    api: tatorapi,
    tator_project: Project,
    media_type: MediaType,
    section: str = "All Media",
    **kwargs,
) -> int:
    """
    Load media from url/local file system to the database
    :param ffmpeg_path: Path to the ffmpeg binary
    :param media_path: Absolute path to the image/video to load
    :param media_url: URL (if hosted)
    :param attributes: Attributes to assign to the media
    :param api: Tator API
    :param tator_project: Tator project
    :param media_type: media type
    :param section: Section to store media in; defaults to "All Media"
    :return:
    """
    info(f"Loading {media_path}")
    spec = gen_spec(
        file_loc=media_path,
        type_id=media_type.id,
        section=section,
        file_url=media_url,
        attributes=attributes,
        **kwargs,
    )
    id = load(
        ffmpeg_path=ffmpeg_path,
        project_id=tator_project.id,
        api=api,
        media_path=media_path,
        spec=spec,
        **kwargs,
    )
    info(f"Loaded {media_path} with id {id}")
    return id


if __name__ == "__main__":
    file_url = "http://localhost:8082/data/cfe/CFE_ISIIS-001-2023-07-12%2009-14-56.898.mp4"
    file_load_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "data" / "cfe" /"CFE_ISIIS-001-2023-07-12 09-14-56.898.mp4"
    api, project = init_api_project("http://localhost:8080", os.getenv("TATOR_TOKEN"), "902111-CFE")
    video_type = find_media_type(api, project.id, "Video")
    load_media(ffmpeg_path='/usr/local/bin/ffmpeg',
               tator_project=project,
               media_url=file_url,
               media_type=video_type,
               attributes={},
               media_path=file_load_path.as_posix(),
               section="cfe_test",
               api=api)
