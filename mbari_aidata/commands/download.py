# mbari_aidata, Apache-2.0 license
# Filename: commands/download.py
# Description: Download a dataset for training detection or classification models

from pathlib import Path

import click

from mbari_aidata import common_args
from mbari_aidata.logger import create_logger_file, info, exception
from mbari_aidata.generators.coco_voc import download as download_full

from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, init_api_project, find_project

# Default values
# The base directory is the same directory as this file
DEFAULT_BASE_DIR = Path.home() / "mbari_aidata" / "datasets"


@click.command(name="dataset", help="Download a dataset for training detection or classification models")
@common_args.token
@common_args.disable_ssl_verify
@common_args.yaml_config
@common_args.version
@click.option(
    "--base-path",
    default=DEFAULT_BASE_DIR,
    type=Path,
    help=f"Path to the base directory to save all data to. Defaults to {DEFAULT_BASE_DIR}",
)
@click.option("--group", help="Group name, e.g. VB250")
@click.option("--depth", type=int, help="Depth, e.g. 200")
@click.option("--section", help="Media section name, e.g. 25000_depth_v1")
@click.option("--min-saliency", type=int, help="Minimum saliency score")
@click.option("--max-saliency", type=int, help="Maximum saliency score")
@click.option("--min-score", type=float, help="Minimum model score")
@click.option("--generator", help="Generator name, e.g. vars-labelbot or vars-annotation")
@click.option("--labels", default="all", help='Comma separated list of labels to download, or "all" for all labels.')
@click.option(
    "--concepts",
    default="all",
    help='Comma separated list of concepts to download, or "all" for all concepts. For legacy projects only',
)
@click.option("--crop-roi", is_flag=True, help="True to download the rois cropped from the original images/video.")
@click.option("--resize", type=int, help="Resize images to this size after cropping them.")
@click.option("--voc", is_flag=True, help="True if export as VOC dataset, False if not.")
@click.option("--coco", is_flag=True, help="True if export as COCO dataset, False if not.")
@click.option("--cifar", is_flag=True, help="True if export as CIFAR dataset, False if not.")
@click.option("--cifar-size", default=32, help="Size of CIFAR images.")
@click.option("--save-score", is_flag=True, help="True to save score in YOLO output, False if not.")
@click.option("--verified", is_flag=True, help="True if only download verified annotations.")
@click.option("--unverified", is_flag=True, help="True if only download not verified annotations.")
@click.option("--single-class", type=str, help="Set to collapse all classes into a single class, e.g. 'marine organism'")
@click.option(
    "--skip-image-download", is_flag=True, help="Skip image download, only download annotations. CIFAR requires images."
)
def download(
    token: str,
    disable_ssl_verify: bool,
    config: str,
    base_path: Path,
    group: str,
    depth: int,
    section: str,
    min_saliency: int,
    max_saliency: int,
    min_score: float,
    version: str,
    generator: str,
    labels: str,
    concepts: str,
    crop_roi: bool,
    resize: int,
    voc: bool,
    cifar: bool,
    coco: bool,
    cifar_size: int,
    save_score: bool,
    single_class: str,
    skip_image_download: bool,
    verified: bool,
    unverified: bool,
) -> bool:
    create_logger_file("download")
    try:
        base_path.mkdir(exist_ok=True, parents=True)
        # Load the configuration file
        config_dict = init_yaml_config(config)
        project = config_dict["tator"]["project"]
        host = config_dict["tator"]["host"]

        # Initialize the Tator API
        api, tator_project = init_api_project(host, token, project, disable_ssl_verify)

        # Find the project
        project = find_project(api, project)
        info(f"Found project id: {project.name} for project {project}")

        # Download a dataset by its version if it has been specified. Combine multiple versions with an underscore.
        if version:
            version_list = version.split(",")
            version_base_name = "_".join([v.strip() for v in version_list])
            data_path = base_path / version_base_name
        else:
            data_path = base_path
        data_path.mkdir(exist_ok=True)
        info(f"Downloading data to {data_path}")

        # Convert comma separated list of concepts to a list
        if labels == "all":
            labels_list = []
        else:
            labels_list = labels.split(",")
            labels_list = [l.strip() for l in labels_list]
            # Check if this is empty
            if len(labels_list) == 1 and labels_list[0] == "":
                labels_list = []
            # Strip off any zero length strings
            labels_list = [l for l in labels_list if len(l) > 0]
        if concepts == "all":
            concepts_list = []
        else:
            concepts_list = concepts.split(",")
            concepts_list = [l.strip() for l in concepts_list]
            # Check if this is empty
            if len(concepts_list) == 1 and concepts_list[0] == "":
                concepts_list = []
            # Strip off any zero length strings
            concepts_list = [c for c in concepts_list if len(c) > 0]

        # Convert comma separated list of versions to a list
        if version:
            version_list = version.split(",")
            version_list = [l.strip() for l in version_list]
        else:
            # If no version is specified, download all versions
            versions = api.get_version_list(project.id)
            version_list = [v.name for v in versions]

        success = download_full(
            api,
            project_id=project.id,
            group=group,
            depth=depth,
            section=section,
            min_saliency=min_saliency,
            max_saliency=max_saliency,
            min_score=min_score,
            version_list=version_list,
            verified=verified,
            unverified=unverified,
            generator=generator,
            output_path=data_path,
            labels_list=labels_list,
            concepts_list=concepts_list,
            single_class=single_class,
            skip_image_download=skip_image_download,
            save_score=save_score,
            cifar_size=cifar_size,
            voc=voc,
            coco=coco,
            cifar=cifar,
            crop_roi=crop_roi,
            resize=resize
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
        base_path=base_path,
        voc=True,
        labels="Acanthamunnopsis milleri,Euphausiacea1,Pyrosoma1,Pyrosoma2",
        concepts="",
        cifar=True,
        coco=True,
        save_score=False,
        skip_image_download=False,
        group="",
        depth="",
        generator="",
        cifar_size=32,
    )
