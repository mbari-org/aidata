# mbari_aidata, Apache-2.0 license
# Filename: tests/test_load_media.py
# Description: Tests loading media to a Tator database
import dotenv
import pytest
from click.testing import CliRunner
from pathlib import Path

from mbari_aidata.__main__ import cli
from mbari_aidata.logger import CustomLogger
import os

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

data_path = Path(__file__).parent / "data"
config_path = Path(__file__).parent / "config"

HAS_DATABASE = False


def setup():
    dotenv.load_dotenv()
    # Print the environment variables
    print(os.environ)
    # TODO: Add a check for the database presence
    if "TATOR_TOKEN" in os.environ.keys():
        global HAS_DATABASE
        HAS_DATABASE = True
    os.environ["ENVIRONMENT"] = "TESTING"

setup()

@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_dryrun():
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
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_video_dryrun():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a video directory"""
    video_path = data_path / "cfe"
    config_yaml = config_path / "config_cfe.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "videos",
            "--input",
            video_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_i2map():
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
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_i2map_txt():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a text listing of image locations"""
    image_listing =  data_path / "i2map_images.txt"
    config_yaml = config_path / "config_i2map.yml"
    print(config_yaml.as_posix())
    args = ["load", "images", "--input", image_listing.as_posix(), "--config", config_yaml.as_posix(), "--token", os.environ["TATOR_TOKEN"]]
    print(' '.join(args))
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_listing.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_cfe():
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
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_cfe_txt():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a text listing of image locations"""
    image_listing =  data_path / "cfe_images.txt"
    config_yaml = config_path / "config_cfe.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_listing.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_uav():
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
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0

@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_uav_txt():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a text listing of image locations"""
    image_listing =  data_path / "uav_images.txt"
    config_yaml = config_path / "config_uav.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_listing.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_planktivore():
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
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0


@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_image_planktivore_txt():
    setup()
    runner = CliRunner()
    """Test that the process command works when passing arguments with a text listing of image locations"""
    image_listing =  data_path / "planktivore_images.txt"
    config_yaml = config_path / "config_planktivore.yml"
    print(config_yaml.as_posix())
    result = runner.invoke(
        cli,
        [
            "load",
            "images",
            "--input",
            image_listing.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0



@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_tracks_i2map_dryrun():
    setup()
    runner = CliRunner()
    # Test loading tracks from an i2MAP tar.gz using dry-run to avoid writes
    tracks_tar = data_path / "i2map" / "i2MAP_20250403T092817Z_1000m_F031_25-tracks.tar.gz"
    config_yaml = config_path / "config_i2map.yml"
    print(config_yaml.as_posix())
    args = [
        "load",
        "tracks",
        "--dry-run",
        "--input",
        tracks_tar.as_posix(),
        "--config",
        config_yaml.as_posix(),
        "--token",
        os.environ["TATOR_TOKEN"],
    ]
    print(' '.join(args))
    result = runner.invoke(cli, args)
    print(result.output)
    assert result.exit_code == 0
