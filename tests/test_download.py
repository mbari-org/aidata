# mbari_aidata, Apache-2.0 license
# Filename: tests/test_download.py
# Description: Tests for the download dataset command

import os
from pathlib import Path

import dotenv
import pytest
from click.testing import CliRunner

from mbari_aidata.__main__ import cli
from mbari_aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

config_path = Path(__file__).parent / "config"

HAS_DATABASE = False


def setup():
    dotenv.load_dotenv()
    if "TATOR_TOKEN" in os.environ:
        global HAS_DATABASE
        HAS_DATABASE = True
    os.environ["ENVIRONMENT"] = "TESTING"


setup()


def test_download_dataset_dry_run_flag_in_help():
    """Test that --dry-run appears in the download dataset help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["download", "dataset", "--help"])
    assert result.exit_code == 0
    assert "--dry-run" in result.output


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_download_dataset_dry_run():
    """Test that download dataset --dry-run queries records but does not write any files."""
    setup()
    import tempfile
    runner = CliRunner()
    config_yaml = config_path / "config_i2map.yml"
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        result = runner.invoke(
            cli,
            [
                "download",
                "dataset",
                "--dry-run",
                "--config",
                config_yaml.as_posix(),
                "--token",
                os.environ["TATOR_TOKEN"],
                "--base-path",
                base_path.as_posix(),
            ],
        )
        print(result.output)
        assert result.exit_code == 0
        # Dry run should not create images/labels directories
        assert not (base_path / "images").exists()
        assert not (base_path / "labels").exists()
