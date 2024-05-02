# aidata, Apache-2.0 license
# Filename: commands/load_boxes.py
# Description: Load boxes from a directory with SDCAT formatted CSV files
import click
from aidata import common_args
from pathlib import Path
from aidata.logger import create_logger_file, info, err
from aidata.plugins.attribute_utils import format_attributes
from aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
from aidata.plugins.loaders.common import init_yaml_config, init_api_project, find_box_type, get_version_id
from aidata.plugins.loaders.tator.localization import gen_spec as gen_localization_spec
from aidata.plugins.loaders.tator.localization import load_bulk_boxes


@click.command("boxes", help="Load boxes from a directory with SDCAT formatted CSV files")
@common_args.token
@common_args.yaml_config
@common_args.dry_run
@common_args.version
@click.option("--input", type=str, required=True, help="input CSV file or path with CSV detection files to load")
@click.option("--max-num", type=int, help="Maximum number of boxes to load")
def load_boxes(token: str, config: str, version: str, input: str, dry_run: bool, max_num: int) -> int:
    """Load boxes from a directory with SDCAT formatted CSV files. Returns the number of boxes loaded."""
    create_logger_file("load_boxes")
    try:
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

        df_boxes = extract_sdcat_csv(input)
        if len(df_boxes) == 0:
            info(f"No boxes found in {input}")
            return 0

        if dry_run:
            info(f"Dry run - not loading {len(df_boxes)} boxes into Tator")
            return 0

        # TODO: add query for box attributes and flag to check if the first spec has all the required attributes

        # Group the detections by image_path
        for image_path, group in df_boxes.groupby("image_path"):
            # Query for the media object with the same name as the image_path - this assumes the image has a unique name
            image_name = Path(image_path).name
            media = api.get_media_list(project=tator_project.id, name=image_name)
            if len(media) == 0:
                print(f"No media found with name {image_name} in project {tator_project.name}.")
                print("Media must be loaded before localizations.")
                continue

            media_id = media[0].id
            specs = []
            max_load = -1 if max_num is None else max_num
            # Create a box for each row in the group
            for index, row in group.iterrows():
                obj = row.to_dict()
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
                if 0 < max_load <= len(specs):
                    break

            info(f"{image_path} boxes {specs}")
            box_ids = load_bulk_boxes(tator_project.id, api, specs)
            info(f"Loaded {len(box_ids)} boxes into Tator for {image_path}")
    except Exception as e:
        err(f"Error: {e}")
        raise e


if __name__ == "__main__":
    import os

    # To run this script, you need to have the TATOR_TOKEN environment variable set and uncomment all @click decorators above
    os.environ["ENVIRONMENT"] = "TESTING"
    test_path = Path(__file__).parent.parent / "tests" / "data" / "i2map"
    yaml_path = Path(__file__).parent.parent / "config" / "config_i2map_local.yml"
    tator_token = os.getenv("TATOR_TOKEN")
    load_boxes(token=tator_token, config=yaml_path.as_posix(), dry_run=False, version="Baseline", input=test_path.as_posix())
