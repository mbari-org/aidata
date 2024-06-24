# aidata, Apache-2.0 license
# Filename: commands/download.py
# Description: Download a dataset for training detection or classification models

from pathlib import Path

import click

from aidata import common_args
from aidata.logger import create_logger_file, info, exception
from aidata.generators.coco import download as download_full

from aidata.plugins.loaders.tator.common import init_yaml_config, init_api_project, find_project

# Default values
# The base directory is the same directory as this file
DEFAULT_BASE_DIR = Path.home() / "aidata" / "datasets"


@click.command(name="dataset", help="Download a dataset for training detection or classification models")
@common_args.token
@common_args.yaml_config
@common_args.version
@click.option("--base-path", default=DEFAULT_BASE_DIR, help=f"Path to the base directory to save all data to. Defaults to {DEFAULT_BASE_DIR}")
@click.option("--group", help="Group name, e.g. VB250")
@click.option("--generator", help="Generator name, e.g. vars-labelbot or vars-annotation")
@click.option("--labels", default="all", help='Comma separated list of labels to download, or "all" for all labels.')
@click.option("--concepts", default="all", help='Comma separated list of concepts to download, or "all" for all concepts. For legacy projects only')
@click.option("--voc", is_flag=True, help="True if export as VOC dataset, False if not.")
@click.option("--coco", is_flag=True, help="True if export as COCO dataset, False if not.")
@click.option("--cifar", is_flag=True, help="True if export as CIFAR dataset, False if not.")
@click.option("--cifar-size", default=32, help="Size of CIFAR images.")
@click.option("--save-score", is_flag=True, help="True to save score in YOLO output, False if not.")
@click.option("--skip-image-download", is_flag=True, help="Skip image download, only download annotations. CIFAR requires images.")
def download(
    token: str,
    config: str,
    base_path: str,
    group: str,
    version: str,
    generator: str,
    labels: str,
    concepts: str,
    voc: bool,
    cifar: bool,
    coco: bool,
    cifar_size: int,
    save_score: bool,
    skip_image_download: bool,
) -> bool:
    create_logger_file("download")
    try:
        base_path = Path(base_path)
        base_path.mkdir(exist_ok=True, parents=True)
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project)

        # Find the project
        project = find_project(api, project)
        info(f"Found project id: {project.name} for project {project}")

        # Download a dataset by its version
        if len(version) > 1:
            version_final = 'combined'
            info(f'Combining datasets {version} into {version_final}')
        else:
            version_final = version[0]
            info(f"Downloading dataset {version_final}")
        data_path = base_path / version_final
        data_path.mkdir(exist_ok=True)

        # Convert comma separated list of concepts to a list
        if labels == "all":
            labels_list = None
        else:
            labels_list = labels.split(",")
            labels_list = [l.strip() for l in labels_list]
            # Check if this is empty
            if len(labels_list) == 1 and labels_list[0] == "":
                labels_list = None
        if concepts == "all":
            concepts_list = None
        else:
            concepts_list = concepts.split(",")
            concepts_list = [l.strip() for l in concepts_list]
            # Check if this is empty
            if len(concepts_list) == 1 and concepts_list[0] == "":
                concepts_list = None

        # Convert comma separated list of versions to a list
        version_list = version.split(",")
        version_list = [l.strip() for l in version_list]


        success = download_full(
            api,
            project_id=project.id,
            group=group,
            version_list=version_list,
            generator=generator,
            output_path=data_path,
            labels_list=labels_list,
            concepts_list=concepts_list,
            skip_image_download=skip_image_download,
            save_score=save_score,
            cifar_size=cifar_size,
            voc=voc,
            coco=coco,
            cifar=cifar,
        )
        return success
    except Exception as e:
        exception(f"Error: {e}")
        return False


if __name__ == "__main__":
    import os

    # To run this script, you need to have the TATOR_TOKEN environment variable set and uncomment all @click decorators above
    # TODO: move this to pytest
    os.environ["ENVIRONMENT"] = "TESTING"
    test_path = Path(__file__).parent.parent.parent / "tests" / "data" / "i2map"
    yaml_path = Path(__file__).parent.parent.parent / "tests" / "config" / "config_i2map.yml"
    base_path = Path(__file__).parent.parent.parent / "tests" / "data" / "download"
    tator_token = os.getenv("TATOR_TOKEN")
    download(
        token=tator_token,
        config=yaml_path.as_posix(),
        version="dino_vits8_20240205_225539,dino_vits8_20240207_022529,dinov2_vits14_hdbscan_",
        base_path=base_path.as_posix(),
        voc=True,
        labels="Acanthamunnopsis milleri,Euphausiacea1,Pyrosoma1,Pyrosoma2",
        concepts="",
        cifar=True,
        coco=True,
        save_score=False,
        skip_image_download=False,
        group="",
        generator="",
        cifar_size=32,
    )
