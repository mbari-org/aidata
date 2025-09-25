# mbari_aidata, Apache-2.0 license
# Filename: common_args.py
# Description: Common arguments for commands

import os
import click

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
    type=str,
    help="Path to a YAML file with project configuration",
)
force = click.option("--force", is_flag=True, help="Force load and skip over check")
dry_run = click.option("--dry-run", is_flag=True, help="Dry run, do not load data")
version = click.option(
    "--version",
    type=str,
    help="Version to load data or download from. Must be provided for loading. Download will default to downloading and merging all versions if not specified.",
)
duplicates = click.option("--check-duplicates", is_flag=True,
                          help="Check if the images are already loaded to avoid duplicates")
disable_ssl_verify = click.option(
    "--disable-ssl-verify",
    is_flag=True,
    help="Disable SSL verification",
)