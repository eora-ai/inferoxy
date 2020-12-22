"""
Entry point of debatch manager
"""
import yaml
import asyncio
import src.data_models as dm
import src.reciever as rc
import src.sender as snd

from loguru import logger
from shared_modules.data_objects import BatchMapping
from src.debatcher import (
    debatch,
    pull_batch_mapping
)


def main():
    """
    Entry point for running main fucntionality
    """
    logger.info('Read config file')
    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)
    logger.info('done')
    logger.info('Run pipeline')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(pipeline(config))


async def pipeline(config: dm.Config):
    """
    Pipeline of debatcher manager
    1) Receive reponse batches
    2) Pull from database batch mapping
    3) Generate from batch and mapping batch response object
    4) Send response object
    """

    # Create sockets for recieving and sending data
    logger.info('Create socket')
    input_socket = rc.create_socket(config=config)
    output_socket = snd.create_socket(config=config)
    logger.info('done')

    # Recieve iterable response batches
    logger.info('Recieving response batches...')
    response_batch_iterable = rc.receive(sock=input_socket)
    logger.info('done')

    # Pulling batch mapping, build response object
    async for response_batch in response_batch_iterable:
        logger.info(f'Pull batch mapping for batch {response_batch.uid}')
        batch_mapping = pull_batch_mapping(
             config=config,
             batch=response_batch
         )

        # Create response objects -> apply main function
        response_objects = debatch(response_batch, batch_mapping)
        for response_object in response_objects:
            await snd.send(output_socket, response_object)


if __name__ == '__main__':
    main()
