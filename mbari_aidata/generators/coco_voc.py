# mbari_aidata, Apache-2.0 license
# Filename: generators/coco_voc.py
# Description: Generate a COCO formatted dataset from a list of media and localizations
import concurrent
import json
import math
import os
from collections import defaultdict
from pathlib import Path
from typing import List

import tator  # type: ignore
import pandas as pd
from PIL import Image
from tqdm import tqdm
from pascal_voc_writer import Writer  # type: ignore
from mbari_aidata.logger import debug, info, err, exception
from mbari_aidata.generators.cifar import create_cifar_dataset
from mbari_aidata.generators.utils import combine_localizations, crop_frame
from tator.openapi.tator_openapi import Localization  

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
    resize: int = 0
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
    :param resize: (optional) Resize images to this size after cropping thems
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

                    # Only keep needed fields to reduce memory usage
                    loc = tator.models.Localization(
                        x=l.x,
                        y=l.y,
                        width=l.width,
                        height=l.height,
                        media=l.media,
                        attributes=l.attributes,
                        id=l.id,
                        frame=l.frame
                    )
                    if single_class:
                        loc.attributes["Label"] = single_class
                    if l.attributes["Label"] not in label_counts.keys():
                        label_counts[l.attributes["Label"]] = 0
                    label_counts[l.attributes["Label"]] += 1
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

        # Count the number of localizations which is the sum of all the localizations for each media
        num_localizations = sum([len(locs) for locs in localizations_by_media_id.values()])

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
                    info(f"Video download not supported yet")
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
                    info(f"Skipping download of {media.name}")

        if crop_roi:

            # Crop the ROI from the original images/video in batches of 500
            batch_size = 500
            scale_filter = ""
            # Prepare for parallel processing  - use all available CPUs
            max_workers = os.cpu_count()
            if resize:
                scale_filter = f"scale={resize}:{resize}"
            for i in range(0, len(all_media), batch_size):
                batch = all_media[i:i + batch_size]
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    crop_tasks = []
                    for media in batch:
                        crop_filter = defaultdict(list)
                        output_maps = defaultdict(list)
                        in_media = localizations_by_media_id[media.id]

                        # Initialize the localizations DataFrame
                        df_localizations = pd.DataFrame([l.to_dict() for l in in_media])
                        df_localizations = df_localizations.sort_values(by=['frame'], ascending=True)

                        # Group by frame, prepare crop arguments
                        for frame, in_frame_loc in df_localizations.groupby('frame'):
                            debug(f"Processing frame {frame} in {media.name}")

                            if len(version_ids) > 1:
                                # Create List of Localization from the Localization
                                loc_list = [Localization(**l) for l in in_frame_loc.to_dict(orient='records')]
                                in_frame_loc = combine_localizations(loc_list)

                            for c in in_frame_loc:
                                crop_id = c.attributes.get("elemental_id", c.id)
                                if c.attributes["Label"]:
                                    output_file = crop_path / c.attributes["Label"] / f"{c.id}.jpg"
                                else:
                                    output_file = crop_path / f"{crop_id}.jpg"
                                if output_file.exists():
                                    continue

                                # Generate crop filter and output map
                                x1 = int(media.width * c.x)
                                y1 = int(media.height * c.y)
                                x2 = int(media.width * (c.x + c.width))
                                y2 = int(media.height * (c.y + c.height))
                                width = x2 - x1
                                height = y2 - y1
                                shorter_side = min(height, width)
                                longer_side = max(height, width)
                                delta = abs(longer_side - shorter_side)

                                padding = delta // 2
                                if width == shorter_side:
                                    x1 -= padding
                                    x2 += padding
                                else:
                                    y1 -= padding
                                    y2 += padding

                                # Ensure coordinates don't go out of bounds
                                x1, x2, y1, y2 = max(0, x1), min(media.width, x2), max(0, y1), min(media.height, y2)

                                if resize:
                                    crop_filter[frame].append(f"crop={x2 - x1}:{y2 - y1}:{x1}:{y1},{scale_filter}")
                                else:
                                    crop_filter[frame].append(f"crop={x2 - x1}:{y2 - y1}:{x1}:{y1}")

                                output_maps[frame].append(f'"{output_file}"')

                        if hasattr(media.media_files, "streaming") and media.media_files.streaming and len(
                                media.media_files.streaming) == 1 and media.media_files.streaming[0].path.startswith(
                                "http"):
                            local_media = media.media_files.streaming[0].path
                            in_media = localizations_by_media_id[media.id]
                            df_localizations = pd.DataFrame([l.to_dict() for l in in_media])
                            df_localizations = df_localizations.sort_values(by=['frame'], ascending=True)

                            for frame, in_frame_loc in df_localizations.groupby('frame'):
                                debug(f"Cropping ROIs in {local_media} frame {frame}")
                                inputs = [
                                    "-y",
                                    "-loglevel", "panic",
                                    "-nostats",
                                    "-hide_banner",
                                    "-ss", frame_to_timestamp(media, frame),
                                    "-i", f'"{local_media}"',
                                    "-vf"
                                ]
                                if len(crop_filter[frame]) == 0:
                                    continue

                                # Submit crop tasks for parallel execution
                                crop_tasks.extend(
                                    [(crop, out, inputs) for crop, out in zip(crop_filter[frame], output_maps[frame])]
                                )
                        else:
                            local_media = (media_path / media.name).as_posix()
                            inputs = [
                                "-y",
                                "-loglevel", "panic",
                                "-nostats",
                                "-hide_banner",
                                "-i", f'"{local_media}"',
                                "-vf"
                            ]
                            debug(f"Cropping ROIs in {local_media} frame {frame}")

                            for frame, in_frame_loc in df_localizations.groupby('frame'):
                                if len(crop_filter[frame]) == 0:
                                    continue

                                # Submit crop tasks for parallel execution
                                crop_tasks.extend(
                                    [(crop, out, inputs) for crop, out in zip(crop_filter[frame], output_maps[frame])]
                                )

                    executor.map(crop_frame, crop_tasks)

        info(f"Finished cropping {num_localizations} ROIs")

        # Create a simple csv file with the media name, cluster, label, score, and label_s and score_s and
        # normalized box coordinates
        with (output_path / "localizations.csv").open("w") as f:
            f.write("media,cluster,saliency,area,label,score,label_s,score_s,x,y,width,height\n")
            for m in all_media:
                media_localizations = localizations_by_media_id[m.id]

                # Add default values for score if missing - this is used to combine localizations
                for loc in media_localizations:
                    if "score" not in loc.attributes:
                        loc.attributes["score"] = 0

                if len(version_ids) > 1:
                    media_localizations = combine_localizations(media_localizations)

                for loc in media_localizations:
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
                            f"{cluster},"
                            f"{saliency},"
                            f"{area},"
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

            # If there is more than one version, we need to combine the localizations
            if len(version_ids) > 1:
                media_localizations = combine_localizations(media_localizations)

            media_lookup_by_id[m.id] = media_path / m.name
            yolo_path = label_path / f"{m.name}.txt"
            image_path = media_path / m.name

            # Get the image size from the image using PIL
            # Skip over any media that are not images
            if not image_path.exists():
                err(f"Could not find {image_path}. Video media not supported yet")
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
                voc_xml_path = voc_path / f"{m.name}.xml"
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
    # Convert timestamp to hour:minute:second format
    total_seconds = frame / media.fps
    hours = math.floor(total_seconds / 3600)
    minutes = math.floor((total_seconds % 3600) / 60)
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


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
