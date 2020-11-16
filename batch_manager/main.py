"""
Entry point of batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio

import yaml
from loguru import logger

import src.data_models as dm
import src.receiver as rc
from src.builder import builder
import src.sender as snd
from src.saver import save_mapping, create_db


async def pipeline(config: dm.Config):
    input_socket = rc.create_socket(config=config)
    output_socket = snd.create_socket(config=config)
    database = create_db(config=config)
    request_object_iterable = rc.receive(input_socket)
    mapping_batch_generator = builder(request_object_iterable)
    logger.info("Start batch manager")
    async for (batch, mapping) in mapping_batch_generator:
        logger.debug(f"Batch completed {batch=}, {mapping=}")
        await snd.send(output_socket, batch)
        save_mapping(database=database, mapping=mapping)


def main():
    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
