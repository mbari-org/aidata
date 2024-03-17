# aidata, Apache-2.0 license
# Filename: common_args.py
# Description: Common arguments for commands
from pathlib import Path

import os
import click

default_yaml_config = Path(os.path.dirname(__file__)) / "config" / "config_uav.yml"
default_yaml_config = Path(os.path.dirname(__file__)) / "config" / "config_bio.yml"

# Common arguments for commands
token = click.option(
    "--token",
    type=str,
    required=True,
    default=os.environ.get("TATOR_TOKEN", None),
)
yaml_config = click.option(
    "--config",
    required=True,
    default=default_yaml_config,
    type=click.Path(exists=True),
    help="Path to a YAML file with project configuration",
)
force = click.option("--force", is_flag=True, help="Force load and skip over check")
dry_run = click.option("--dry-run", is_flag=True, help="Dry run, do not load data")
version = click.option(
    "--version",
    type=str,
    default="Baseline",
    help="Version to load data into. Default is 'Baseline'",
)
