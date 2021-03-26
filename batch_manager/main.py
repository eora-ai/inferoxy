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

import src.sender as snd
import src.receiver as rc
import src.data_models as dm
from src.builder import builder
from src.saver import save_mapping


async def pipeline(config: dm.Config):
    """
    Main pipeline of batch manager

    Parameters
    ----------
    config
        Config object
    """
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

    Path(config.db_file).mkdir(parents=True, exist_ok=True)
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
