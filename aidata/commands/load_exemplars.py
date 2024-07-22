# aidata, Apache-2.0 license
# Filename: commands/load_exemplars.py
# Description: Load image embedding vectors from a SDCAT formatted CSV exemplar file
import click
import redis

from aidata import common_args
from aidata.logger import create_logger_file, info, err
from aidata.plugins.extractors.tap_sdcat_csv import extract_sdcat_csv
from aidata.plugins.loaders.tator.common import init_yaml_config
from aidata.predictors.process_vits import ProcessVITS
from pathlib import Path


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
@click.option("--reset", is_flag=True, help="Reset the database before loading. Use with caution!")
@click.option(
    "--label",
    type=str,
    help="Class label for the exemplars. This is used as the base class name for the "
    "exemplar images, e.g. Otter_0, Otter_1, etc.",
)
def load_exemplars(config: str, input: Path, dry_run: bool, label: str, device: str, batch_size, reset: bool = False) -> int:
    """Load embeddings from a directory with SDCAT formatted exemplar CSV files. Returns the number of exemplar image
    embeddings loaded."""
    create_logger_file("load_exemplars")
    num_exemplars = 0
    try:
        # Load the configuration file
        # Each project needs a separate redis server for exemplar embeddings - this
        # is done through separate ports
        config_dict = init_yaml_config(config)
        redi_host = config_dict["redis"]["host"]
        redi_port = config_dict["redis"]["port"]
        info(f"Connecting to REDIS server at {redi_host}:{redi_port}")
        r = redis.Redis(host=redi_host, port=redi_port)
        vits_processor = ProcessVITS(r, device=device, reset=reset, batch_size=batch_size)

        info(f"Loading exemplars from {input}")
        # If input is a directory, load the first CSV file found
        if Path(input).is_dir():
            input = list(Path(input).rglob("*.csv"))[0]
        df = extract_sdcat_csv(input)

        if dry_run:
            info(f"Dry run mode. No data will be loaded. Found {len(df)} exemplars")
            return len(df)

        info(f"Processing {len(df)} exemplars")
        image_paths = df.image_path.unique().tolist()  # noqa
        info(f"Found {len(image_paths)} unique exemplar images")

        # If image paths are relative, prepend the base path to the image paths
        if not Path(image_paths[0]).is_absolute():
            base_path = Path(input).parent
            image_paths = [os.path.join(base_path, p) for p in image_paths]

        # Class names are indexed, e.g. Otter_0, Otter_1, etc.
        # Each class name corresponds to an exemplar image that represents a subcluster
        class_names = [f"{label}_{i}" for i in range(len(image_paths))]
        info(f"Loading {len(image_paths)} exemplar images with class names {class_names}")
        vits_processor.load(image_paths, class_names)
        num_exemplars = len(image_paths)
    except Exception as e:
        err(f"Error: {e}")
        raise e

    return num_exemplars


if __name__ == "__main__":
    import os
    from pathlib import Path

    # To run this script, uncomment all @click decorators above
    os.environ["ENVIRONMENT"] = "TESTING"

    test_path = Path(__file__).parent.parent.parent / "tests" / "data" / "uav" / "otterexemplars.csv"
    yaml_path = Path(__file__).parent.parent.parent / "tests" / "config" / "config_uav.yml"
    load_exemplars(
        config=yaml_path.as_posix(), dry_run=False, input=test_path.as_posix(), label="Otter", batch_size=32, reset=True
    )
