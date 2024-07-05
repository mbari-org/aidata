# aidata, Apache-2.0 license
# Filename: __main__.py
# Description: Main entry point for the aidata command line interface
from datetime import datetime
from pathlib import Path

import pytz
import click
import sys


sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path

from aidata.commands.download import download
from aidata.commands.load_images import load_images
from aidata.commands.load_exemplars import load_exemplars
from aidata.logger import err, info

from aidata import __version__
from aidata.commands.load_queue import load_queue
from aidata.commands.load_boxes import load_boxes

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
    Commands related to loading data
    """
    pass


cli.add_command(cli_load)
cli_load.add_command(load_images)
cli_load.add_command(load_boxes)
cli_load.add_command(load_queue)
cli_load.add_command(load_exemplars)


@click.group(name="download")
def cli_download():
    """
    Commands related to downloading data
    """
    pass


cli.add_command(cli_download)
cli_download.add_command(download)

if __name__ == "__main__":
    try:
        start = datetime.now(pytz.utc)
        cli()
        end = datetime.now(pytz.utc)
        info(f"Done. Elapsed time: {end - start} seconds")
    except Exception as e:
        err(f"Exiting. Error: {e}")
        exit(-1)
