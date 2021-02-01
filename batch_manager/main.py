"""
Entry point of batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from datetime import datetime

import yaml
from pathlib import Path
from loguru import logger
import src.data_models as dm
import src.receiver as rc
from src.builder import builder
import src.sender as snd
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
    path_log = "/tmp/batch_manager"
    path_input = "/tmp/batch_manager/input"
    path_output = "/tmp/batch_manager/result"
    path_db = "/tmp/batch_manager/db"

    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    Path(path_log).mkdir(parents=True, exist_ok=True)
    Path(path_input).touch()
    Path(path_output).touch()
    Path(path_db).touch()

    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
