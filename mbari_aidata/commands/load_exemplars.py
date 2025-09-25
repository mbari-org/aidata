# mbari_aidata, Apache-2.0 license
# Filename: commands/load_exemplars.py
# Description: Load image embedding vectors from a SDCAT formatted CSV exemplar file
import click
import redis
import re

from mbari_aidata import common_args
from mbari_aidata.logger import create_logger_file, info, err
from mbari_aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config, init_api_project, find_box_type
from mbari_aidata.predictors.process_vits import ViTWrapper
from pathlib import Path


def parse_id(input_str):
    """Parse the database id from the image name, e.g. 12467345 from 12467345.1.jpg or 12467345.jpg, etc.
    If no id is found, return the input string"""
    match = re.match(r"^\d+", input_str)
    if match:
        return match.group(0)
    return input_str


@click.command("exemplars", help="Load exemplars from a SDCAT formatted CSV exemplar file into a REDIS server")
@common_args.yaml_config
@common_args.dry_run
@click.option(
    "--input",
    type=Path,
    required=True,
    help="input CSV file with SDCAT formatted CSV exemplar file, or a directory with SDCAT formatted CSV exemplar files",
)
@click.option("--device", type=str, default="cpu", help="Device to use for processing, e.g. cuda:0 or cpu")
@click.option("--label", type=str, help="Class label for the exemplars")
@click.option("--batch-size", type=int, default=32, help="Batch size for loading embeddings")
@click.option("--password", type=str, required=True, help="Password for the REDIS server")
@click.option(
    "--label",
    type=str,
    help="Class label for the exemplars. This is used as the base class name for the "
    "exemplar images, e.g. Otter:0, Otter:1, etc.",
)
def load_exemplars(config: str, input: Path, dry_run: bool, label: str, device: str, batch_size, password: str) -> int:
    """Load embeddings from a directory with SDCAT formatted exemplar CSV files. Returns the number of exemplar image
    embeddings loaded."""
    create_logger_file("load_exemplars")
    try:
        # Load the configuration file
        # Each project needs a separate redis server for exemplar embeddings - this
        # is done through separate ports
        config_dict = init_yaml_config(config)
        redis_host = config_dict["redis"]["host"]
        redis_port = config_dict["redis"]["port"]
        model = config_dict["vss"]["model"]
        info(f"Connecting to REDIS server at {redis_host}:{redis_port}")
        r = redis.Redis(host=redis_host, port=redis_port, password=password)
        vits = ViTWrapper(r, model_name=model, device=device, batch_size=batch_size)

        info(f"Loading exemplars from {input}")
        # If input is a directory, load the first CSV file found
        if Path(input).is_dir():
            info(f"Input is a directory. Searching for CSV files found")
            csv_files = list(Path(input).rglob("*.csv"))
            if len(csv_files) == 0:
                err(f"No CSV files found in {input}")
                return 0
            input = csv_files[0]
        else:
            info(f"Input is a file: {input}")
            if not Path(input).exists():
                err(f"File {input} does not exist")
                return 0

        df = extract_sdcat_csv(input)

        if dry_run:
            info(f"Dry run mode. No data will be loaded. Found {len(df)} exemplars")
            return len(df)

        info(f"Processing {len(df)} exemplars")
        image_paths = df.image_path.unique().tolist()  # noqa
        info(f"Found {len(image_paths)} unique exemplar images")

        if len(image_paths) == 0:
            err(f"No image paths found in the input CSV file {input}")
            return 0

        # If image paths are relative, prepend the base path to the image paths
        if not Path(image_paths[0]).is_absolute():
            base_path = Path(input).parent
            image_paths = [os.path.join(base_path, p) for p in image_paths]

        df['id'] = df['image_path'].apply(lambda x: parse_id(Path(x).stem))
        ids = df['id'].tolist()
        class_names = [f"{label}:{i}" for i in ids]
        info(f"Loading {len(image_paths)} exemplar images with class names {class_names}")
        vits.load(image_paths, class_names)
        num_exemplars = len(image_paths)

        return num_exemplars
    except Exception as e:
        err(f"Error: {e}")
        raise e



if __name__ == "__main__":
    import os
    from pathlib import Path

    # To run this script, uncomment all @click decorators above
    os.environ["ENVIRONMENT"] = "TESTING"
    password = os.getenv("REDIS_PASSWORD")
    test_path = Path(__file__).parent.parent.parent / "tests" / "data" / "uav" / "otterexemplars.csv"
    yaml_path = Path(__file__).parent.parent.parent / "tests" / "config" / "config_uav.yml"
    load_exemplars(
        config=yaml_path.as_posix(), dry_run=False, input=test_path.as_posix(), label="Otter", batch_size=32, reset=True,
        password=password, device="cpu",
    )
