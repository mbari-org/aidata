# aidata, Apache-2.0 license
# Filename: commands/db_utils.py
# Description: Miscellaneous functions for working with the database


import click
import redis

from aidata import common_args
from aidata.logger import create_logger_file, info
from aidata.plugins.loaders.tator.common import init_yaml_config
from aidata.predictors.process_vits import ViTWrapper


@click.command("reset", help="Reset the REDIS server")
@common_args.yaml_config
@click.option("--redis-password", type=str, required=True, help="Password for the REDIS server")
def reset_redis(redis_password: str, config: str) -> bool:
    """Reset the REDIS database."""
    try:
        # Load the configuration file
        # Each project needs a separate redis server for exemplar embeddings - this
        # is done through separate ports
        config_dict = init_yaml_config(config)
        redis_host = config_dict["redis"]["host"]
        redis_port = config_dict["redis"]["port"]
        info(f"Connecting to REDIS server at {redis_host}:{redis_port}")
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        ViTWrapper(r, reset=True)
        info("Redis server reset")
        return True
    except Exception as e:
        info(f"Error resetting REDIS server: {e}")
        return False
