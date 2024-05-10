from click.testing import CliRunner
from pathlib import Path

from aidata.__main__ import cli
from aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

data_path = Path(__file__).parent / "data"
config_path = Path(__file__).parent / "config"


def setup():
    # Make sure the TATOR_TOKEN environment variable is set
    import os

    assert "TATOR_TOKEN" in os.environ, "TATOR_TOKEN environment variable must be set"
    os.environ["ENVIRONMENT"] = "Testing"


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


def test_load_boxes_i2map():
    setup()
    csv_path = data_path / "i2map" / "16-06-06T16_38_18-200m-F041_25000.csv"
    config_yaml = config_path / "config_i2map.yml"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "load",
            "boxes",
            "--input",
            csv_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0


def test_load_boxes_i2map_version():
    setup()
    csv_path = data_path / "i2map" / "16-06-06T16_38_18-200m-F041_25000.csv"
    config_yaml = config_path / "config_i2map.yml"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "load",
            "boxes",
            "--input",
            csv_path.as_posix(),
            "--version",
            "Baseline",
            "--config",
            config_yaml.as_posix(),
        ],
    )
    print(result.output)
    assert result.exit_code == 0
