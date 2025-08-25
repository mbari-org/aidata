# mbari_aidata, Apache-2.0 license
# Filename: tests/test_load_annotations.py
# Description: Tests loading annotations to a Tator database
import os

import dotenv
import pytest
from click.testing import CliRunner
from pathlib import Path

from mbari_aidata.__main__ import cli
from mbari_aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

data_path = Path(__file__).parent / "data"
config_path = Path(__file__).parent / "config"

HAS_DATABASE = False


def setup():
    # Make sure the TATOR_TOKEN environment variable is set
    import os
    dotenv.load_dotenv()

    # TODO: Add a check for the database presence
    assert "TATOR_TOKEN" in os.environ, "TATOR_TOKEN environment variable must be set"
    os.environ["ENVIRONMENT"] = "TESTING"


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
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
            "--token",
            os.environ["TATOR_TOKEN"],
            "--version",
            "Baseline"
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
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
            "--token",
            os.environ["TATOR_TOKEN"],
            "--version",
            "Baseline"
        ],
    )
    print(result.output)
    assert result.exit_code == 0
