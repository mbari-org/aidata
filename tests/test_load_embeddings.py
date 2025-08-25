# mbari_aidata, Apache-2.0 license
# Filename: tests/test_load_embeddings.py
# Description: Tests loading embeddings to a Redis database with RediSearch
import os
import dotenv
import pytest
import redis
from click.testing import CliRunner
from pathlib import Path

from mbari_aidata.__main__ import cli
from mbari_aidata.logger import CustomLogger
from mbari_aidata.plugins.loaders.tator.common import init_yaml_config

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

data_path = Path(__file__).parent / "data"
config_path = Path(__file__).parent / "config"

HAS_DATABASE = False


def setup():
    dotenv.load_dotenv()
    config_dict = init_yaml_config(config_path / "config_uav.yml")
    redis_host = config_dict["redis"]["host"]
    redis_port = config_dict["redis"]["port"]
    connection = redis.Redis(host=redis_host, port=redis_port, password=os.environ["REDIS_PASSWORD"])

    try:
        if connection.ping():
            global HAS_DATABASE
            HAS_DATABASE = True
    except redis.exceptions.ConnectionError:
        pass

setup()

@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_exemplars_dryrun():
    runner = CliRunner()
    """Test that the load command works when passing arguments to dry run"""
    csv_path = data_path / "uav"
    config_yaml = config_path / "config_uav.yml"
    result = runner.invoke(
        cli,
        [
            "load",
            "exemplars",
            "--dry-run",
            "--password", os.environ["REDIS_PASSWORD"],
            "--label", "Otter",
            "--input",
            csv_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0

@pytest.mark.skipif(not HAS_DATABASE, reason="This test is excluded because it requires a database")
def test_load_exemplar():
    runner = CliRunner()
    """Test that the load command works when passing arguments to dry run"""
    csv_path = data_path / "uav"
    config_yaml = config_path / "config_uav.yml"
    result = runner.invoke(
        cli,
        [
            "load",
            "exemplars",
            "--password", os.environ["REDIS_PASSWORD"],
            "--label", "Otter",
            "--input",
            csv_path.as_posix(),
            "--config",
            config_yaml.as_posix(),
            "--token",
            os.environ["TATOR_TOKEN"]
        ],
    )
    print(result.output)
    assert result.exit_code == 0