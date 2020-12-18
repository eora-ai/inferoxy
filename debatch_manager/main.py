"""
Entry point of debatch manager
"""
import yaml
import src.data_models as dm
import src.reciever as rc
import src.sender as snd

from loguru import logger
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
    pipeline(config)


def pipeline(config: dm.Config):

    # Create sockets for recieving and sending data
    logger.info('Create socket')
    input_socket = rc.create_socket(config=config)
    output_socket = snd.create_socket(config=config)
    logger.info('done')

    # Recieve iterable response batches
    logger.info('Recieving response batches...')
    response_batch_iterable = rc.receive(sock=input_socket)
    logger.info('done')

    # Pulling batch mappings
    for response_batch in response_batch_iterable:
        logger.info(f'Pull batch mapping for batch {response_batch.uid}')
        batch_mapping = pull_batch_mapping(
            config=config,
            batch=response_batch
        )
        print(batch_mapping)
