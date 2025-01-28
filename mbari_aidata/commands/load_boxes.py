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
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, find_box_type, init_api_project, get_version_id


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
            max_load = -1 if max_num is None else max_num
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
