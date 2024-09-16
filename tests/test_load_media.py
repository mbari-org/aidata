# aidata, Apache-2.0 license
# Filename: tests/test_load_media.py
# Description: Tests loading media to a Tator database

import pytest
from click.testing import CliRunner
from pathlib import Path

from aidata.__main__ import cli
from aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

data_path = Path(__file__).parent / "data"
config_path = Path(__file__).parent / "config"

HAS_DATABASE = False


def setup():
    # Make sure the TATOR_TOKEN environment variable is set
    import os

    # TODO: Add a check for the database presence
    if "TATOR_TOKEN" in os.environ.keys():
        global HAS_DATABASE
        HAS_DATABASE = True
    os.environ["ENVIRONMENT"] = "TESTING"

setup()

@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_media_dryrun():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a single image"""
    image_path = data_path / "i2map"
    config_yaml = config_path / "config_i2map.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--dry-run",
            "--input",
            image_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_media_i2map():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a single image"""
    image_path = data_path / "i2map"
    config_yaml = config_path / "config_i2map.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_media_cfe():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a single image"""
    image_path = data_path / "cfe"
    config_yaml = config_path / "config_cfe.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_media_uav():
    runner = CliRunner()
    """Test that the process command works when passing arguments with a single image"""
    image_path = data_path / "uav"
    config_yaml = config_path / "config_uav.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_media_planktivore():
    runner = CliRunner()
    """Test that the process command works when passing arguments with a single image"""
    image_path = data_path / "planktivore"
    config_yaml = config_path / "config_planktivore.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0