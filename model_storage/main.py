"""
Entry point of model storage
"""
__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import asyncio
import argparse

import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger

from src.connector import Connector  # type: ignore
from src.database import Redis  # type: ignore
import src.data_models as dm  # type: ignore
from shared_modules.parse_config import build_config


async def pipeline(config: dm.Config):
    """
    Main pipeline of model storage

    Parameters
    ---------
    config
        Config of zmq
    config_db
        Config of remote database
    """

    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind(config.address)
    logger.debug(f"CONFIG DB {config.database}")
    logger.debug(type(config.database))

    database = Redis(config.database)
    connector = Connector(database)

    logger.info("Start listening")
    while True:
        model_slug = await socket.recv()
        model = connector.fetch_model_obj(model_slug.decode("utf-8"))
        logger.info(f"Build model object {model}")
        await socket.send_pyobj(model)


def main():
    """
    Entry point of model storage
    run asyncio pipeline
    """

    parser = argparse.ArgumentParser(description="Model storage process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/model_storage.yaml",
    )
    args = parser.parse_args()
    config = build_config(args.config, "model_storage")

    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
