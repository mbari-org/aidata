# aidata, Apache-2.0 license
# Filename: plugins/generators/coco.py
# Description: Generate a COCO formatted dataset from a list of media and localizations
import json
from pathlib import Path

import numpy as np
import tator
from PIL import Image
from tqdm import tqdm
from pascal_voc_writer import Writer
from aidata.logger import debug, info, err, exception
from aidata.generators.cifar import create_cifar_dataset
from aidata.generators.utils import combine_localizations


def download(
    api: tator.api,
    project_id: int,
    group: str,
    version_list: [],
    generator: str,
    output_path: Path,
    labels_list: [] = None,
    concepts_list: [] = None,
    cifar_size: int = 32,
    skip_image_download: bool = False,
    save_score: bool = False,
    voc: bool = False,
    coco: bool = False,
    cifar: bool = False,
) -> bool:
    """
    Download a dataset based on a version tag for training
    :param api: tator.api
    :param project_id: project id
    :param group: group name
    :param version_list: version name(s), e.g. ['Baseline'] to download
    :param generator: generator name, e.g. 'vars-labelbot' or 'vars-annotation'
    :param output_path: output directory to save the dataset
    :param labels_list: (optional) list of labels to download
    :param concepts_list: (optional) list of labels to download
    :param cifar_size: (optional) size of the CIFAR images
    :param skip_image_download: (optional) True if the images should not be downloaded
    :param save_score: (optional) True if the score should be saved in the YOLO format
    :param voc: (optional) True if the dataset should also be stored in VOC format
    :param coco: (optional) True if the dataset should also be stored in COCO format
    :param cifar: (optional) True if the dataset should also be stored in CIFAR format
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

        attribute = []
        num_concept_records = {}
        num_label_records = {}
        num_records = 0
        if generator:
            attribute = [f"generator::{generator}"]
        if group:
            attribute += [f"group::{group}"]

        if concepts_list:
            for concept in concepts_list:
                num_concept_records[concept] = api.get_localization_count(project=project_id, version=version_ids, attribute_contains=[f'concept::{concept}']+attribute)
                num_records += num_concept_records[concept]
        if labels_list:
            for label in labels_list:
                num_label_records[label] = api.get_localization_count(project=project_id, version=version_ids, attribute_contains=[f'Label::{label}']+attribute)
                num_records += num_label_records[label]
        if not concepts_list and not labels_list:
            num_records = api.get_localization_count(project=project_id, version=version_ids)

        info(
            f'Found {num_records} records for version {version_list} and generator {generator}, group {group} and '
            f"including {labels_list if labels_list else 'everything'} "
        )

        if num_records == 0:
            info(
                f'Could not find any records for version {version_list} and generator {generator}, group {group} and '
                f"including {labels_list if labels_list else 'everything'} "
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

        if voc:
            info(f"Creating VOC files in {voc_path}")
        if coco:
            coco_path = output_path / "coco"
            coco_path.mkdir(exist_ok=True)
            info(f"Creating COCO files in {coco_path}")

        localizations = []

        def query_localizations(prefix: str, query_str: str, max_records: int):
            inc = min(5000, max_records)
            for start in range(0, max_records, inc):
                info(f"Query records {start} to {start + inc} using attribute filter {attribute} {prefix} {query_str}")

                new_localizations = api.get_localization_list(
                    project=project_id, attribute_contains=[f'{prefix}::{query_str}']+attribute,
                    version=version_ids, start=start, stop=start + 5000
                )
                if len(new_localizations) == 0:
                    break
                localizations.extend(new_localizations)

        if concepts_list:
            for concept in concepts_list:
                query_localizations('concept', concept, num_concept_records[concept])
        if labels_list:
            for label in labels_list:
                query_localizations('Label', label, num_label_records[label])
        if not concepts_list and not labels_list:
            query_localizations('', '', num_records)

        info(f"Found {len(localizations)} records for version {version_list}, generator {generator}, group {group} and including {labels_list if labels_list else 'everything'}")
        info(f"Creating output directory {output_path} in YOLO format")

        media_lookup_by_id = {}

        # Get all the unique media ids in the localizations
        media_ids = list(set([l.media for l in localizations]))

        # Get all the media objects at those ids
        all_media = get_media(api, project_id, media_ids)

        # Get all the unique media names
        def get_media_stem(media_path: Path) -> str:
            parts = Path(media_path.name).stem.rsplit(".", 1)
            return ".".join(parts)

        media_names = list(set([get_media_stem(m) for m in all_media]))

        # Get all the unique Label attributes and sort them alphabetically
        labels = list(sorted(set([l.attributes["Label"] for l in localizations])))

        # Write the labels to a file called labels.txt
        with (output_path / "labels.txt").open("w") as f:
            for label in labels:
                f.write(f"{label}\n")

        if not skip_image_download:
            # Download all the media files - this needs to be done before we can create the VOC/CIFAR files which reference the
            # media file size
            for media in tqdm(all_media, desc="Downloading", unit="iteration"):
                out_path = media_path / media.name
                if not out_path.exists():
                    info(f"Downloading {media.name} to {out_path}")
                    num_tries = 0
                    success = False
                    while num_tries < 3 and not success:
                        try:
                            for progress in tator.util.download_media(api, media, out_path):
                                debug(f"{media.name} download progress: {progress}%")
                            success = True
                        except Exception as e:
                            err(e)
                            num_tries += 1
                    if num_tries == 3:
                        err(f"Could not download {media.name}")
                        exit(-1)

        # Create YOLO, and optionally COCO, CIFAR, or VOC formatted files
        info(f"Creating YOLO files in {label_path}")
        json_content = {}

        for media_name in tqdm(media_names, desc="Creating VOC formats", unit="iteration"):
            # Get the media object
            media = [m for m in all_media if get_media_stem(m) == media_name][0]

            # Get all the localizations for this media
            media_localizations = [l for l in localizations if l.media == media.id]

            # If there is more than one version, we need to combine the localizations
            if len(version_ids) > 1:
                media_localizations = combine_localizations(media_localizations)

            media_lookup_by_id[media.id] = media_path / media.name
            yolo_path = label_path / f"{media_name}.txt"
            image_path = media_path / media.name

            # Get the image size from the image using PIL
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
                voc_xml_path = voc_path / f"{media_name}.xml"
                image_path = (media_path / media.name).as_posix()

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

                    writer.addObject(loc.attributes["Label"], x1, y1, x2, y2)

                # Write the file
                writer.save(voc_xml_path.as_posix())

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

            images, labels = create_cifar_dataset(cifar_size, cifar_path, media_lookup_by_id, localizations, labels)
            np.save(cifar_path / "images.npy", images)
            np.save(cifar_path / "labels.npy", labels)

        if coco:
            info(f"Creating COCO data in {coco_path}")
            with (coco_path / "coco.json").open("w") as f:
                json.dump(json_content, f, indent=2)

        return True
    except Exception as e:
        exception(e)
        return False


def get_media(api: tator.api, project_id: int, media_ids: []):
    """
    Get media from a project
    :param api: tator.api
    :param project_id: project id
    :param media_ids: List of media ids
    """
    try:
        medias = []
        for start in range(0, len(media_ids), 200):
            new_medias = api.get_media_list(project=project_id, media_id=media_ids[start : start + 200])
            medias = medias + new_medias
        return medias
    except Exception as e:
        err(e)
        return None
