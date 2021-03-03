"""
Entry point of model storage
"""
__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import asyncio  # type: ignore

import yaml
import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger

from src.connector import Connector  # type: ignore
import src.data_models as dm  # type: ignore


async def pipeline(config_db: dm.DatabaseConfig):
    """
    Main pipeline of model storage

    Parameters
    ---------
    config
        Config of zmq
    config_db
        Config of remote database
    """
    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)

    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind(config_dict["address"])

    connector = Connector(config_db)

    logger.info("Start listening")
    while True:
        model_slug = await socket.recv()
        model = connector.fetch_model(model_slug.decode("utf-8"))
        logger.info(f"Build model object {model}")
        await socket.send_pyobj(model)


def main():
    """
    Entry point of model storage
    run asyncio pipeline
    """

    config_db = dm.DatabaseConfig(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dbname=os.environ.get("DB_NAME"),
    )

    asyncio.run(pipeline(config_db))


if __name__ == "__main__":
    main()
