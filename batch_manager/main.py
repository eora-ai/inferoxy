"""
Entry point of batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

from loguru import logger
from envyaml import EnvYAML     # type: ignore

import src.sender as snd
import src.receiver as rc
import src.data_models as dm
from src.builder import builder
from src.saver import save_mapping
from shared_modules.parse_config import build_config_file


async def pipeline(config: dm.Config):
    """
    Main pipeline of batch manager

    Parameters
    ----------
    config
        Config object
    """
    logger.debug(config)
    logger.debug(f"Input {config.zmq_input_address}")
    logger.debug(f"Output {config.zmq_output_address}")
    input_socket = rc.create_socket(config=config)
    output_socket = snd.create_socket(config=config)
    request_object_iterable = rc.receive(input_socket)
    mapping_batch_generator = builder(request_object_iterable, config=config)
    logger.info("Start batch manager")
    async for (batch, mapping) in mapping_batch_generator:
        batch.status = dm.Status.CREATED
        batch.created_at = datetime.now()
        logger.debug(f"Batch completed {batch=}, {mapping=}")
        await snd.send(output_socket, batch)
        save_mapping(config=config, mapping=mapping)


def update_config(config, config_path):
    env = EnvYAML(config_path, strict=False)
    config.zmq_input_address = env["zmq_input_address"]
    config.zmq_output_address = env["zmq_output_address"]
    config.db_file = env["db_file"]
    config.create_db_file = env["create_db_file"]
    config.send_batch_timeout = env["send_batch_timeout"]
    return config


def main():
    """
    Entry point run asyncio pipeline
    """
    # Set up log level of logger
    log_level = os.getenv("LOGGING_LEVEL")
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    parser = argparse.ArgumentParser(description="Batch manager process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/batch_manager.yaml",
    )
    args = parser.parse_args()

    config = dm.Config.parse_file(args.config, content_type="yaml")

    env_config_path = build_config_file(config, args.config, "batch_manager")

    config = update_config(config, env_config_path)

    Path(config.db_file).mkdir(parents=True, exist_ok=True)
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
