# mbari_aidata, Apache-2.0 license
# Filename: __main__.py
# Description: Main entry point for the mbari_aidata command line interface
from datetime import datetime
from pathlib import Path

import pytz
import click
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path

from mbari_aidata.commands.load_clusters import load_clusters
from mbari_aidata.commands.download import download
from mbari_aidata.commands.load_images import load_images
from mbari_aidata.commands.load_video import load_video
from mbari_aidata.commands.load_exemplars import load_exemplars
from mbari_aidata.commands.db_utils import reset_redis
from mbari_aidata.commands.transform import transform, voc_to_yolo
from mbari_aidata.logger import err, info

from mbari_aidata import __version__
from mbari_aidata.commands.load_queue import load_queue
from mbari_aidata.commands.load_boxes import load_boxes

if "LOG_PATH" not in locals():
    LOG_PATH = Path.home().as_posix()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", message="%(prog)s, version %(version)s")
def cli():
    """
    Load data to tator database from a command line.
    """
    pass


@click.group(name="load")
def cli_load():
    """
    Load data, such as images, boxes, and exemplars into either a Postgres or REDIS database
    """
    pass


cli.add_command(cli_load)
cli_load.add_command(load_images)
cli_load.add_command(load_video)
cli_load.add_command(load_boxes)
cli_load.add_command(load_queue)
cli_load.add_command(load_exemplars)
cli_load.add_command(load_clusters)


@click.group(name="download")
def cli_download():
    """
    Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format
    """
    pass


cli.add_command(cli_download)
cli_download.add_command(download)


@click.group(name="db")
def cli_db():
    """
    Commands related to database management
    """
    pass


cli.add_command(cli_db)
cli_db.add_command(reset_redis)


@click.group(name="transform")
def cli_transform():
    """
    Commands related to transforming downloaded data
    """
    pass


cli.add_command(cli_transform)
cli_transform.add_command(transform)
cli_transform.add_command(voc_to_yolo)

if __name__ == "__main__":
    try:
        start = datetime.now(pytz.utc)
        cli()
        end = datetime.now(pytz.utc)
        info(f"Done. Elapsed time: {end - start} seconds")
    except Exception as e:
        err(f"Exiting. Error: {e}")
        exit(-1)
