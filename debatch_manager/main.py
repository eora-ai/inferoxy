"""
Entry point of debatch manager
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import sys
import asyncio
import argparse
from pathlib import Path

from loguru import logger
from envyaml import EnvYAML     # type: ignore

import src.sender as snd
import src.receiver as rc
import src.data_models as dm
from src.debatcher import debatch, pull_batch_mapping
from shared_modules.parse_config import build_config_file


def update_config(config, config_path):
    env = EnvYAML(config_path, strict=False)
    config.zmq_input_address = env["zmq_input_address"]
    config.zmq_output_address = env["zmq_output_address"]
    config.db_file = env["db_file"]
    config.create_db_file = env["create_db_file"]
    config.send_batch_mapping_timeout = env["send_batch_mapping_timeout"]
    return config


def main():
    """
    Entry point for running main fucntionality
    """
    # Set up log level of logger
    log_level = os.getenv("LOGGING_LEVEL")
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    logger.info("Read config file")

    parser = argparse.ArgumentParser(description="Debatch manager process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/debatch_manager.yaml",
    )
    args = parser.parse_args()

    config = dm.Config.parse_file(args.config, content_type="yaml")

    config_path_env = build_config_file(config, args.config, "debatch_manager")

    config = update_config(config, config_path_env)

    Path(config.zmq_input_address.replace("ipc://", "")).parent.mkdir(
        exist_ok=True, parents=True
    )
    Path(config.zmq_output_address.replace("ipc://", "")).parent.mkdir(
        exist_ok=True, parents=True
    )

    logger.info("Configs loaded")
    logger.info("Run pipeline")

    asyncio.run(pipeline(config))


async def pipeline(config: dm.Config):
    """
    Pipeline of debatcher manager
    1) Receive reponse batches
    2) Pull from database batch mapping
    3) Generate from batch and mapping batch response object
    4) Send response object
    """

    # Create sockets for recieving and sending data
    logger.info("Create socket")
    input_socket = rc.create_socket(config=config)
    output_socket = snd.create_socket(config=config)
    logger.info("done")

    # Recieve iterable response batches
    logger.info("Recieving response batches...")
    response_batch_iterable = rc.receive(sock=input_socket)

    # Pulling batch mapping, build response object
    async for response_batch in response_batch_iterable:
        logger.info(f"Pull batch mapping for batch {response_batch.uid}")

        sleep_time = config.send_batch_mapping_timeout
        batch_mapping = None

        while True:
            try:
                batch_mapping = pull_batch_mapping(config=config, batch=response_batch)
                break
            except IOError as exc:
                logger.debug(f"Database locked try in {sleep_time}")
                await asyncio.sleep(float(sleep_time))
            except TypeError as exc:
                logger.exception(f"Mapping doesnot exists for {response_batch=}")
                break

        if batch_mapping is None:
            continue

        # Create response objects -> apply main function
        response_objects = debatch(response_batch, batch_mapping)
        for response_object in response_objects:
            logger.debug(f"Try to send {response_object}")
            await snd.send(output_socket, response_object)
            logger.debug(f"{response_object} was sent")


if __name__ == "__main__":
    main()
