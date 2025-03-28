# mbari_aidata, Apache-2.0 license
# Filename: commands/load_boxes.py
# Description: Load boxes from a directory with SDCAT formatted CSV files
import click
from mbari_aidata import common_args
from pathlib import Path
from mbari_aidata.logger import create_logger_file, info, err
from mbari_aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
from mbari_aidata.plugins.extractors.tap_voc import extract_voc
from mbari_aidata.plugins.loaders.tator.localization import gen_spec as gen_localization_spec
from mbari_aidata.plugins.loaders.tator.localization import load_bulk_boxes
from mbari_aidata.plugins.loaders.tator.attribute_utils import format_attributes
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, find_box_type, find_media_type, init_api_project, get_version_id
from mbari_aidata.plugins.loaders.tator.media import get_media_ids

@click.command("boxes", help="Load boxes from a directory with VOC or SDCAT formatted CSV files")
@common_args.token
@common_args.yaml_config
@common_args.dry_run
@common_args.version
@click.option("--exclude", type=str, help="Exclude boxes with this label", multiple=True)
@click.option("--input", type=Path, required=True, help=" VOC xml or SDCAT formatted CSV files")
@click.option("--max-num", type=int, help="Maximum number of boxes to load")
@click.option("--min-score", type=float, help="Minimum score to load between 0 and 1")
def load_boxes(token: str, config: str, version: str, input: Path, dry_run: bool, max_num: int, min_score:float, exclude: str) -> int:
    """Load boxes from a directory with VOC or SDCAT formatted CSV files. Returns the number of boxes loaded."""

    try:
        create_logger_file("load_boxes")
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project)
        box_type = find_box_type(api, tator_project.id, "Box")
        image_type = find_media_type(api, tator_project.id, "Image")
        version_id = get_version_id(api, tator_project, version)
        box_attributes = config_dict["tator"]["box"]["attributes"]
        assert box_type is not None, f"No box type found in project {project}"
        assert version_id is not None, f"No version found in project {project}"

        # Determine whether to use sdcat or voc format based on the file extension
        valid_extensions = [".csv", ".xml"]
        extractors = {"csv": extract_sdcat_csv, 'xml': extract_voc}
        df_boxes = []
        if input.is_dir():
            # Search for files with valid extensions
            files = list(input.rglob("*"))
            valid_files = [f for f in files if f.suffix in valid_extensions]
            if len(valid_files) == 0:
                err(f"No valid files found in {input}")
                return 0
            # Use the first valid file and its extension to determine the extractor
            first_file = valid_files[0]
            if first_file.suffix in valid_extensions:
                extractor = extractors[first_file.suffix[1:]]
                df_boxes = extractor(input)
        else:
            # Use the extension of the file to determine the extractor
            extractor = extractors[input.suffix[1:]]
            df_boxes = extractor(input)

        if len(df_boxes) == 0:
            info(f"No boxes found in {input}")
            return 0

        min_score = 0 if min_score is None else min_score
        df_boxes = df_boxes[df_boxes["score"] >= min_score]

        if dry_run:
            info(f"Dry run - not loading {len(df_boxes)} boxes into Tator")
            return 0

        # TODO: add query for box attributes and flag to check if the first spec has all the required attributes

        # If we are missing the label column, try to create one from the class column
        if "class" in df_boxes.columns and "label" not in df_boxes.columns:
            df_boxes = df_boxes.rename(columns={"class": "label"})

        max_load = -1 if max_num is None else max_num
        # If missing x,y,xx,xy columns default to the entire image, this means one box per image
        # in this case we need to load the media first and then the boxes as it is more efficient for bulk loading
        if "x" not in df_boxes.columns and "y" not in df_boxes.columns and "xy" not in df_boxes.columns and "xy" not in df_boxes.columns:
            df_boxes["x"] = 0
            df_boxes["y"] = 0
            df_boxes["xx"] = 1.
            df_boxes["xy"] = 1.
            media_map = get_media_ids(api, tator_project, image_type.id) # TODO: Add support for kwargs to refine this query

            # Load in bulk 1000 boxes at a time
            box_count = len(df_boxes)
            batch_size = min(1000, box_count)
            num_loaded = 0
            for i in range(0, box_count, batch_size):
                df_batch = df_boxes[i:i + batch_size]
                specs = []
                for index, row in df_batch.iterrows():
                    obj = row.to_dict()
                    if exclude is not None:
                        if obj["label"] in exclude:
                            continue
                    image_name = Path(obj["image_path"]).name
                    if image_name not in media_map.keys():
                        info(f"No media found with name {image_name} in project {tator_project.name}.")
                        info("Media must be loaded before localizations.")
                        continue
                    attributes = format_attributes(obj, box_attributes)
                    specs.append(
                        gen_localization_spec(
                            box=[obj["x"], obj["y"], obj["xx"], obj["xy"]],
                            version_id=version_id,
                            label=obj["label"],
                            width=obj["image_width"],
                            height=obj["image_height"],
                            attributes=attributes,
                            frame_number=0,
                            type_id=box_type.id,
                            media_id=media_map[image_name],
                            project_id=tator_project.id,
                            normalize=False,  # sdcat is already normalized between 0-1
                        )
                    )
                # Truncate the boxes if the max number of boxes to load is set
                if 0 < max_load <= len(specs):
                    specs = specs[:max_load]

                box_ids = load_bulk_boxes(tator_project.id, api, specs)
                info(f"Loaded {len(box_ids)} boxes of {box_count} into Tator")

                # Update the number of boxes loaded and finish if the max number of boxes to load is set
                num_loaded += len(box_ids)
                if 0 < max_load <= num_loaded:
                    break
        else:
            # Group the detections by image_path
            for image_path, group in df_boxes.groupby("image_path"):
                # Query for the media object with the same name as the image_path - this assumes the image has a unique name
                image_name = Path(image_path).name  # type: ignore
                media = api.get_media_list(project=tator_project.id, name=image_name)
                if len(media) == 0:
                    info(f"No media found with name {image_name} in project {tator_project.name}.")
                    info("Media must be loaded before localizations.")
                    continue

                media_id = media[0].id
                specs = []
                num_loaded = 0
                # Create a box for each row in the group
                for index, row in group.iterrows():
                    obj = row.to_dict()
                    if exclude is not None:
                        if obj["label"] in exclude:
                            continue
                    attributes = format_attributes(obj, box_attributes)
                    specs.append(
                        gen_localization_spec(
                            box=[obj["x"], obj["y"], obj["xx"], obj["xy"]],
                            version_id=version_id,
                            label=obj["label"],
                            width=obj["image_width"],
                            height=obj["image_height"],
                            attributes=attributes,
                            frame_number=0,
                            type_id=box_type.id,
                            media_id=media_id,
                            project_id=tator_project.id,
                            normalize=False,  # sdcat is already normalized between 0-1
                        )
                    )

                # Truncate the boxes if the max number of boxes to load is set
                if 0 < max_load <= len(specs):
                    specs = specs[:max_load]

                info(f"{image_path} boxes {specs}")
                box_ids = load_bulk_boxes(tator_project.id, api, specs)
                info(f"Loaded {len(box_ids)} boxes into Tator for {image_path}")

                # Update the number of boxes loaded and finish if the max number of boxes to load is set
                num_loaded += len(box_ids)
                if 0 < max_load <= num_loaded:
                    break
    except Exception as e:
        err(f"Error: {e}")
        raise e

    return len(df_boxes)


if __name__ == "__main__":
    import os

    # To run this script, you need to have the TATOR_TOKEN environment variable set and uncomment all @click decorators above
    os.environ["ENVIRONMENT"] = "TESTING"
    test_path = Path(__file__).parent.parent.parent / "tests" / "data" / "i2map"
    yaml_path = Path(__file__).parent.parent.parent / "tests" / "config" / "config_i2map.yml"
    tator_token = os.getenv("TATOR_TOKEN")
    load_boxes(
        token=tator_token, config=yaml_path.as_posix(), dry_run=False, version="Baseline", input=test_path, max_num=10
    )
