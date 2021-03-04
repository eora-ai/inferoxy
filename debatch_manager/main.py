"""
Entry point of debatch manager
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import sys
import asyncio
from pathlib import Path

import yaml
from loguru import logger

import src.sender as snd
import src.receiver as rc
import src.data_models as dm
from src.debatcher import debatch, pull_batch_mapping


def main():
    """
    Entry point for running main fucntionality
    """
    # Set up log level of logger
    log_level = os.getenv("LOGGING_LEVEL")
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    logger.info("Read config file")

    path_dir_debatch = "/tmp/debatch_manager"
    path_dir_task = "/tmp/task_manager"

    path_input = "/tmp/task_manager/result"
    path_output = "/tmp/debatch_manager/result"
    path_db = "/tmp/debatch_manager/db"

    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    Path(path_dir_debatch).mkdir(parents=True, exist_ok=True)
    Path(path_dir_task).mkdir(parents=True, exist_ok=True)
    Path(path_input).touch()
    Path(path_output).touch()
    Path(path_db).touch()

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
                await asyncio.sleep(sleep_time)
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
