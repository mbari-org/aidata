# mbari_aidata, Apache-2.0 license
# Filename: generators/coco_voc.py
# Description: Generate a COCO formatted dataset from a list of media and localizations
import concurrent
import json
import math
import os
from collections import defaultdict
from pathlib import Path
from typing import List, Optional

import tator  # type: ignore
import pandas as pd
from PIL import Image
from tqdm import tqdm
from pascal_voc_writer import Writer  # type: ignore
from mbari_aidata.logger import debug, info, err, exception
from mbari_aidata.generators.cifar import create_cifar_dataset
from mbari_aidata.generators.utils import build_roi_crop_filter, combine_localizations, crop_frame, crop_frame_multi
from tator.openapi.tator_openapi import Localization  

def resolve_external_video_file(root: Path, media_name: str) -> Optional[Path]:
    stem = Path(media_name).stem
    for ext in (".avi", ".mov", ".mp4"):
        filename = f"{stem}{ext}"

        # Fast path: direct child of root
        direct = root / filename
        if direct.is_file():
            return direct

        # Recursive search (user requested): prefer the first match in a stable order.
        # Note: rglob order is filesystem-dependent; sorting makes it deterministic.
        matches = sorted(root.rglob(filename))
        for m in matches:
            if m.is_file():
                return m
    return None

def download(
    api: tator.api,
    project_id: int,
    group: str,
    depth: int,
    section: str,
    version_list: List[str],
    verified: bool,
    unverified: bool,
    generator: str,
    output_path: Path,
    labels_list: List[str],
    concepts_list: List[str],
    cifar_size: int = 32,
    single_class: str = None,
    skip_image_download: bool = False,
    min_saliency: int = None,
    max_saliency: int = None,
    min_score: float = 0.0,
    save_score: bool = False,
    voc: bool = False,
    coco: bool = False,
    cifar: bool = False,
    crop_roi: bool = False,
    external_video_root: Optional[Path] = None,
    resize: int = 0,
    fill: Optional[str] = None,
) -> bool:
    """
    Download a dataset based on a version tag for training
    :param api: tator.api
    :param project_id: project id
    :param group: group name
    :param depth: depth, e.g. 200
    :param media_type: media datatype, 'video' or 'image'
    :param section: media section name, e.g. 25000_depth_v1
    :param min_saliency: minimum saliency score, e.g. 500
    :param max_saliency: maximum saliency score, e.g. 500
    :param min_score: minimum model score, e.g. 0.5
    :param version_list: version name(s), e.g. ['Baseline'] to download
    :param verified: (optional) True if only verified annotations should be downloaded
    :param unverified: (optional) True if only unverified annotations should be downloaded
    :param generator: generator name, e.g. 'vars-labelbot' or 'vars-annotation'
    :param output_path: output directory to save the dataset
    :param labels_list: (optional) list of labels to download
    :param concepts_list: (optional) list of labels to download
    :param cifar_size: (optional) size of the CIFAR images
    :param single_class: (optional) set to collapse all classes into a single class, e.g. 'marine organism'
    :param skip_image_download: (optional) True if the images should not be downloaded
    :param save_score: (optional) True if the score should be saved in the YOLO format
    :param voc: (optional) True if the dataset should also be stored in VOC format
    :param coco: (optional) True if the dataset should also be stored in COCO format
    :param cifar: (optional) True if the dataset should also be stored in CIFAR format
    :param crop_roi: (optional) True if the dataset should crop the ROI from the original images
    :param external_video_root: (optional) Directory containing source videos for ROI cropping. For a given
        Tator media item, the stem is matched and <stem>.mov is preferred, else <stem>.mp4.
    :param resize: (optional) Resize images to this size after cropping thems
    :param fill: (optional) Fill color (``black`` or ``white``) for squaring ROI crops near image edges
    :return: True if the dataset was created successfully, False otherwise
    """
    try:
        # Get the version
        versions = api.get_version_list(project=project_id)
        debug(versions)

        # Find the version by name
        version_ids = [v.id for v in versions if v.name in version_list]
        if len(version_ids) != len(version_list):
            err(f"Could not find all versions {version_list}")
            return False

        num_concept_records = {}
        num_label_records = {}
        num_records = 0
        # Prepare attributes based on provided values
        attribute_equals = []
        attribute_gt = []
        attribute_lt = []
        related_attribute_equals = []
        if generator:
            attribute_equals.append(f"generator::{generator}")
        if group:
            attribute_equals.append(f"group::{group}")
        if verified:
            attribute_equals.append("verified::true")
        if unverified:
            attribute_equals.append("verified::false")
        if depth:
            related_attribute_equals.append(f"depth::{depth}")
        if section:
            related_attribute_equals.append(f"section::{section}")
        if min_saliency:
            attribute_gt.append(f"saliency::{min_saliency}")
        if max_saliency:
            attribute_lt.append(f"saliency::{max_saliency}")
        if min_score:
            attribute_gt.append(f"score::{min_score}")

        # Helper function to get localization count with common arguments
        def get_localization_count(concept_or_label=None):
            kwargs = {}
            if concept_or_label:
                kwargs["attribute_contains"] = [concept_or_label]
            if len(attribute_equals) > 0:
                kwargs["attribute"] = attribute_equals
            if len(attribute_gt) > 0:
                kwargs["attribute_gt"] = attribute_gt
            if len(attribute_lt) > 0:
                kwargs["attribute_lt"] = attribute_lt
            if len(related_attribute_equals) > 0:
                kwargs["related_attribute"] = related_attribute_equals
            info(f"Getting localization count with {kwargs}")
            return api.get_localization_count(
                project=project_id,
                version=version_ids,
                **kwargs
            )
        # Process concepts list
        for concept in concepts_list:
            num_concept_records[concept] = get_localization_count(f"concept::{concept}")
            num_records += num_concept_records[concept]

        # Process labels list
        for label in labels_list:
            num_label_records[label] = get_localization_count(f"Label::{label}")
            num_records += num_label_records[label]

        # Handle case where both lists are empty
        if not concepts_list and not labels_list:
            num_records = get_localization_count()


        info(
            f"Found {num_records} records for version {version_list} and generator {generator}, "
            f"group {group}, min_saliency {min_saliency}, min_score {min_score},"
            f" verified {verified} and including {labels_list if labels_list else 'everything'} "
        )

        if num_records == 0:
            info(
                f"Could not find any records for version {version_list} and generator {generator}, "
                f"group {group}, min_saliency {min_saliency}, min_score {min_score},"
                f" verified {verified} and including {labels_list if labels_list else 'everything'}"
            )
            return False

        # Create the output directory in the expected format that deepsea-ai expects for training
        # See https://docs.mbari.org/deepsea-ai/data/ for more information
        label_path = output_path / "labels"
        label_path.mkdir(exist_ok=True)
        media_path = output_path / "images"
        media_path.mkdir(exist_ok=True)
        voc_path = output_path / "voc"
        voc_path.mkdir(exist_ok=True)
        crop_path = output_path / "crops"
        crop_path.mkdir(exist_ok=True)

        if voc:
            info(f"Creating VOC files in {voc_path}")
        if coco:
            coco_path = output_path / "coco"
            coco_path.mkdir(exist_ok=True)
            info(f"Creating COCO files in {coco_path}")

        label_counts = {} # To capture label counts

        # Get all the media objects that match the criteria
        localizations_by_media_id = {}
        def get_medias(concept_or_label=None):
            kwargs = {}
            if concept_or_label:
                kwargs["related_attribute_contains"] = [concept_or_label]
            if len(attribute_equals) > 0:
                kwargs["related_attribute"] = attribute_equals
            if len(attribute_gt) > 0:
                kwargs["related_attribute_gt"] = attribute_gt
            if len(attribute_lt) > 0:
                kwargs["related_attribute_lt"] = attribute_lt
            if depth:
                kwargs["attribute"] = [f"depth::{depth}"]
            if section:
                if "attribute_contains" in kwargs:
                    kwargs["attribute_contains"].append(f"section::{section}")
                kwargs["attribute_contains"] = [f"section::{section}"]
            info(f"Getting media with {kwargs}")
            medias = api.get_media_list(project=project_id, **kwargs)
            info(f"Found {len(medias)} media objects that match the criteria {kwargs}")
            return medias

        for concept in concepts_list:
            medias = get_medias(f"concept::{concept}")
            for media in medias:
                localizations_by_media_id[media.id] = []
        for label in labels_list:
            medias = get_medias(f"Label::{label}")
            for media in medias:
                localizations_by_media_id[media.id] = []
        if not concepts_list and not labels_list:
            medias = get_medias()
            for media in medias:
                localizations_by_media_id[media.id] = []

        def query_localizations(prefix: str, query_str: str, max_records: int):
            # set inc to 5000 or max_records-1 or 1, whichever is larger
            if max_records == 0:
                return
            if max_records == 1:
                inc = 1
            else:
                inc = min(5000, max_records - 1)

            kwargs = {}
            for start in range(0, max_records, inc):

                if attribute_equals:
                    kwargs["attribute"] = attribute_equals
                if prefix:
                    kwargs["attribute_contains"] = [f"{prefix}::{query_str}"]
                if attribute_gt:
                    kwargs["attribute_gt"] = attribute_gt
                if attribute_lt:
                    kwargs["attribute_lt"] = attribute_lt

                info(f"Query records {start} to {start + inc} using {kwargs} {prefix} {query_str}")

                new_localizations = api.get_localization_list(
                    project=project_id,
                    start=start,
                    stop=start + 5000,
                    version=version_ids,
                    **kwargs
                )
                if len(new_localizations) == 0:
                    break

                for l in new_localizations:
                    # Remove any localization objects that are not tator.models.Localization; this is a bug in the api?
                    if not isinstance(l, tator.models.Localization):
                        continue

                    if l.media not in localizations_by_media_id.keys():
                        continue

                    # Override the score if more than one version is being used for verified labels.
                    # This helps propagate the human verified label via NMS
                    if len(version_ids) > 1 and l.attributes.get("verified", False) == verified:
                        l.attributes["score"] = 1

                    # Only keep needed fields to reduce memory usage
                    loc = tator.models.Localization(
                        x=l.x,
                        y=l.y,
                        width=l.width,
                        height=l.height,
                        media=l.media,
                        attributes=l.attributes,
                        id=l.id,
                        frame=l.frame,
                        elemental_id=l.elemental_id,
                    )
                    if single_class:
                        loc.attributes["Label"] = single_class

                    # Append the localization to the media
                    localizations_by_media_id[l.media].append(loc)

        if concepts_list:
            for concept in concepts_list:
                query_localizations("concept", concept, num_concept_records[concept])
        if labels_list:
            for label in labels_list:
                query_localizations("Label", label, num_label_records[label])
        if not concepts_list and not labels_list:
            query_localizations("", "", num_records)

        # Remove any media objects that do not have localizations
        for media_id in list(localizations_by_media_id.keys()):
            if len(localizations_by_media_id[media_id]) == 0:
                localizations_by_media_id.pop(media_id)

        # Run NMS on the localizations for each media if there are multiple versions
        if len(version_ids) > 1:
            for media_id, locs in localizations_by_media_id.items():
                # Group by frame, combine localizations per frame
                df_localizations = pd.DataFrame([l.to_dict() for l in locs])
                for frame, in_frame_loc in df_localizations.groupby('frame'):
                    # Convert in_frame_loc to List[Localization]
                    tmp_locs = []
                    for _, row in in_frame_loc.iterrows():
                        loc = Localization(
                            x=row['x'],
                            y=row['y'],
                            width=row['width'],
                            height=row['height'],
                            media=row['media'],
                            attributes=row.get('attributes', {}),
                            id=row['id'],
                            frame=row['frame'],
                            elemental_id=row.get('elemental_id', None),
                        )
                        tmp_locs.append(loc)
                    combined_locs = combine_localizations(tmp_locs)
                    localizations_by_media_id[media_id] = combined_locs

        # Count the number of labels and num_localizations
        num_localizations = 0
        for locs in localizations_by_media_id.values():
            for loc in locs:
                label = loc.attributes.get("Label", "Unknown")
                if label not in label_counts:
                    label_counts[label] = 0
                label_counts[label] += 1
                num_localizations += 1

        info(
            f"Found {num_localizations} records for version {version_list}, generator {generator}, "
            f"group {group}, depth {depth}, section {section}, and including {labels_list if labels_list else 'everything'}"
        )
        info(f"Creating output directory {output_path} in YOLO format")

        media_lookup_by_id = {}

        # Get all the media objects at those ids
        media_ids = list(localizations_by_media_id.keys())

        # Get the media objects in chunks of 200
        all_media = []
        for start in range(0, len(media_ids), 200):
            media = get_media(api, project_id, media_ids[start: start + 200])
            # Remove any objects that are not tator.models.Media; this is a bug in the api?
            new_media = [m for m in media if isinstance(m, tator.models.Media)]
            all_media += new_media

        # Write the labels to a file called labels.txt
        labels = list(label_counts.keys())
        with (output_path / "labels.txt").open("w") as f:
            for label in labels:
                f.write(f"{label}\n")

        # If cropping the ROI, create the output directories and write stats to a file
        if crop_roi:
            for label in label_counts.keys():
                (crop_path / label).mkdir(exist_ok=True)

            with (crop_path / "stats.json").open("w") as f:
                json.dump({"total_labels": label_counts}, f, indent=4, sort_keys=True)

        if not skip_image_download:
            # Download all the media files - this needs to be done before we can create the
            # VOC/CIFAR files which reference the media file size
            for media in tqdm(all_media, desc="Downloading", unit="iteration"):
                out_path = media_path / media.name
                if '.mp4' in media.name:
                    continue
                if not out_path.exists() or out_path.stat().st_size == 0:
                    info(f"Downloading {media.name} to {out_path}")
                    num_tries = 0
                    success = False
                    while num_tries < 3 and not success:
                        try:
                            for progress in tator.util.download_media(api, media, out_path):
                                debug(f"{media.name} download progress: {progress}%")
                            success = True
                        except Exception as e:
                            err(str(e))
                            num_tries += 1
                    if num_tries == 3:
                        err(f"Could not download {media.name}")
                        exit(-1)
                else:
                    debug(f"Skipping download of {media.name}")

        if crop_roi:
            info(f"Cropping {num_localizations} ROIs...")
            max_workers = os.cpu_count()

            # Build all potential crop tasks across all media before filtering
            all_crop_tasks = []  # (output_file, filter_str, output_str, inputs)
            for media in all_media:
                if media.id not in localizations_by_media_id:
                    continue
                in_media = localizations_by_media_id[media.id]
                df_localizations = pd.DataFrame([l.to_dict() for l in in_media])
                df_localizations = df_localizations.sort_values(by=['frame'], ascending=True)

                crop_filter = defaultdict(list)
                output_maps = defaultdict(list)
                output_files_map = defaultdict(list)

                if media.width is None or media.height is None:
                    err(f"Media {media.name} has no width or height")
                    continue
                mw, mh = media.width, media.height
                _resize = resize or 0

                for frame, in_frame_loc in df_localizations.groupby('frame'):
                    debug(f"Processing frame {frame} in {media.name}")
                    for row_loc in in_frame_loc.itertuples(index=False):
                        crop_id = row_loc.elemental_id if row_loc.elemental_id else row_loc.id
                        attrs = row_loc.attributes if isinstance(row_loc.attributes, dict) else {}
                        label = attrs.get("Label", "Unknown")
                        output_file = crop_path / label / f"{crop_id}.jpg" if label else crop_path / f"{crop_id}.jpg"

                        x1 = int(mw * row_loc.x)
                        y1 = int(mh * row_loc.y)
                        x2 = int(mw * (row_loc.x + row_loc.width))
                        y2 = int(mh * (row_loc.y + row_loc.height))
                        filter_str = build_roi_crop_filter(x1, y1, x2, y2, mw, mh, resize=_resize, fill=fill)
                        if not filter_str:
                            continue

                        crop_filter[frame].append(filter_str)
                        output_maps[frame].append(str(output_file))
                        output_files_map[frame].append(output_file)

                # Resolve the crop source for this media.
                # - If external_video_root is set, use it (stem match; .mov preferred, else .mp4 or .avi)
                # - Else if Tator provides a streaming HTTP URL, use that
                # - Else use the locally-downloaded media under media_path
                if external_video_root is not None:
                    resolved = resolve_external_video_file(external_video_root, media.name)
                    if resolved is None:
                        err(
                            f"External crop source not found for {media.name}. "
                            f"Expected {Path(media.name).stem}.mov, {Path(media.name).stem}.mp4 or {Path(media.name).stem}.avi in {external_video_root}"
                        )
                        continue
                    crop_source = resolved.as_posix()
                    is_video_source = True
                elif (
                    hasattr(media.media_files, "streaming")
                    and media.media_files.streaming
                    and len(media.media_files.streaming) == 1
                    and media.media_files.streaming[0].path.startswith("http")
                ):
                    crop_source = media.media_files.streaming[0].path
                    is_video_source = True
                else:
                    crop_source = (media_path / media.name).as_posix()
                    is_video_source = Path(media.name).suffix.lower() in {".mp4", ".mov", ".avi"}

                for frame in crop_filter:
                    if len(crop_filter[frame]) == 0:
                        continue
                    # Build base inputs up to -i <source>; -vf/-filter_complex is added by crop_frame_multi
                    base_inputs = ["-y", "-loglevel", "error", "-nostats", "-hide_banner"]
                    if is_video_source:
                        base_inputs.extend(["-ss", frame_to_timestamp(media, frame)])
                    base_inputs.extend(["-i", crop_source])
                    debug(f"Cropping ROIs in {crop_source} frame {frame}")
                    inputs_key = tuple(base_inputs)
                    for crop, out, output_file in zip(crop_filter[frame], output_maps[frame], output_files_map[frame]):
                        all_crop_tasks.append((output_file, crop, out, inputs_key))

            # Skip tasks whose output already exists — single tqdm pass over all tasks
            pending_tasks = [
                (crop, out, inputs_key)
                for output_file, crop, out, inputs_key in tqdm(all_crop_tasks, desc="Checking existing crops", unit="crop")
                if not output_file.exists()
            ]
            skipped = len(all_crop_tasks) - len(pending_tasks)
            info(f"Cropping {len(pending_tasks)} ROIs ({skipped} already exist)...")

            # Group by (source, frame) so each unique seek becomes one ffmpeg invocation
            frame_groups: dict = {}
            for crop, out, inputs_key in pending_tasks:
                if inputs_key not in frame_groups:
                    frame_groups[inputs_key] = []
                frame_groups[inputs_key].append((crop, out))

            frame_task_args = [(list(inputs_key), pairs) for inputs_key, pairs in frame_groups.items()]
            info(f"Executing {len(frame_task_args)} ffmpeg frame groups ({len(pending_tasks)} crops) across {max_workers} workers...")

            with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                list(tqdm(executor.map(crop_frame_multi, frame_task_args), total=len(frame_task_args), desc="Cropping frames", unit="frame"))

        info(f"Finished cropping {num_localizations} ROIs")

        # Create a simple csv file with the media name, cluster, etc. and normalized box coordinates
        with (output_path / "localizations.csv").open("w") as f:
            f.write("media,frame,uuid,verified,cluster,saliency,area,predicted_label,label,score,label_s,score_s,x,y,width,height\n")
            for m in all_media:
                media_localizations = localizations_by_media_id[m.id]

                for loc in media_localizations:
                    uuid = loc.elemental_id
                    frame = loc.frame
                    verified = loc.attributes.get("verified", False)
                    predicted_label = loc.attributes.get("predicted_label", "Unknown")
                    label = loc.attributes.get("Label", "Unknown")
                    score = loc.attributes.get("score", 0)
                    score_s = loc.attributes.get("score_s", 0)
                    label_s = loc.attributes.get("label_s", "Unknown")
                    cluster = loc.attributes.get("cluster", "Unknown")
                    area = loc.attributes.get("area", -1)
                    saliency = loc.attributes.get("saliency", -1)
                    x = loc.x
                    y = loc.y
                    width = loc.width
                    height = loc.height
                    f.write(f"{m.name},"
                            f"{frame},"
                            f"{uuid},"
                            f"{verified},"
                            f"{cluster},"
                            f"{saliency},"
                            f"{area},"
                            f"{predicted_label},"
                            f"{label},{score},"
                            f"{label_s},{score_s},"
                            f"{x},{y},{width},{height}\n")

        info(f'Finished creating {output_path / "localizations.csv"}')

        # Create YOLO, and optionally COCO, CIFAR, or VOC formatted files
        info(f"Creating YOLO files in {label_path}")
        json_content = {}

        for m in tqdm(all_media, desc="Creating VOC formats", unit="iteration"):
            # Get all the localizations for this media
            media_localizations = localizations_by_media_id[m.id]

            media_lookup_by_id[m.id] = media_path / m.name
            yolo_path = label_path / f"{m.name}.txt"
            image_path = media_path / m.name

            # Get the image size — use PIL for images, Tator metadata for video
            _VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv"}
            is_video = Path(m.name).suffix.lower() in _VIDEO_EXTS

            if is_video:
                if m.width is None or m.height is None:
                    err(f"No dimensions on media {m.name}, skipping")
                    continue
                image_width, image_height = m.width, m.height
            else:
                if not image_path.exists():
                    err(f"Could not find {image_path}")
                    continue
                image = Image.open(image_path)
                image_width, image_height = image.size

            with yolo_path.open("w") as f:
                for loc in media_localizations:
                    # Get the label index
                    label_idx = labels.index(loc.attributes["Label"])

                    # Get the bounding box which is normalized to a 0-1 range and centered
                    x = loc.x + loc.width / 2
                    y = loc.y + loc.height / 2
                    w = loc.width
                    h = loc.height
                    if save_score:
                        f.write(f"{label_idx} {x} {y} {w} {h} {loc.attributes['score']}\n")
                    else:
                        f.write(f"{label_idx} {x} {y} {w} {h}\n")

            # optionally create VOC files
            if voc:
                # Paths to the VOC file and the image
                voc_xml_path = voc_path / f"{Path(m.name).stem}.xml"
                image_path = (media_path / m.name).as_posix()

                writer = Writer(image_path, image_width, image_height)

                # Add localizations
                for loc in media_localizations:
                    # Get the bounding box which is normalized to the image size and upper left corner
                    x1 = loc.x
                    y1 = loc.y
                    x2 = loc.x + loc.width
                    y2 = loc.y + loc.height

                    x1 *= image_width
                    y1 *= image_height
                    x2 *= image_width
                    y2 *= image_height

                    x1 = int(round(x1))
                    y1 = int(round(y1))
                    x2 = int(round(x2))
                    y2 = int(round(y2))

                    writer.addObject(loc.attributes["Label"], x1, y1, x2, y2, pose=str(loc.id))

                # Write the file
                writer.save(voc_xml_path.as_posix())

                # Replace the xml tag pose with uuid
                with open(voc_xml_path, "r") as file:
                    filedata = file.read()
                filedata = filedata.replace("pose", "id")
                with open(voc_xml_path, "w") as file:
                    file.write(filedata)

            if coco:
                coco_localizations = []
                # Add localizations
                for loc in media_localizations:
                    # Get the bounding box which is normalized to the image size and upper left corner
                    x = loc.x
                    y = loc.y
                    w = loc.x + loc.width
                    h = loc.y + loc.height

                    x *= image_width
                    y *= image_height
                    w *= image_width
                    h *= image_height

                    x = int(round(x))
                    y = int(round(y))
                    w = int(round(w))
                    h = int(round(h))

                    # optionally add to COCO formatted dataset
                    coco_localizations.append(
                        {
                            "concept": loc.attributes["Label"],
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                        }
                    )

                json_content[yolo_path.as_posix()] = coco_localizations

        # optionally create a CIFAR formatted dataset
        if cifar:
            cifar_path = output_path / "cifar"
            cifar_path.mkdir(exist_ok=True)
            info(f"Creating CIFAR data in {cifar_path}")

            success = create_cifar_dataset(cifar_size, cifar_path, media_lookup_by_id, localizations_by_media_id, labels)
            if not success:
                err("Could not create CIFAR data")
                return False

        if coco:
            info(f"Creating COCO data in {coco_path}")
            with (coco_path / "coco.json").open("w") as f:
                json.dump(json_content, f, indent=2)

        return True
    except Exception as e:
        exception(str(e))
        return False


def frame_to_timestamp(media: tator.models.Media, frame: int) -> str:
    fps = getattr(media, "fps", None) or 0
    if not fps:
        fps = 30.0
    total_seconds = frame / fps
    total_microseconds = int(total_seconds * 1_000_000)
    return f"{total_microseconds}us"


def get_media(api: tator.api, project_id: int, media_ids: List[int]) -> List[tator.models.Media]:
    """
    Get media from a project
    :param api: tator.api
    :param project_id: project id
    :param media_ids: List of media ids
    """
    medias = [tator.models.Media]
    try:
        for start in range(0, len(media_ids), 200):
            new_medias = api.get_media_list(project=project_id, media_id=media_ids[start : start + 200])
            medias = medias + new_medias
        return medias
    except Exception as e:
        err(str(e))
        return medias
