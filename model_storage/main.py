"""
Entry point of model storage
"""
__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import asyncio
import argparse

import yaml
import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger

from src.connector import Connector  # type: ignore
from src.database import Redis  # type: ignore
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
    parser = argparse.ArgumentParser(description="Model storage process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/model_storage.yaml",
    )
    args = parser.parse_args()

    with open(args.config) as config_file:
        config_dict = yaml.full_load(config_file)

    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind(config_dict["address"])

    database = Redis(config_db)
    connector = Connector(database)

    try:
        connector.load_models()
    except FileNotFoundError:
        pass
    logger.info("Load models from /etc/inferoxy/models.yaml")

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

    config_db = dm.DatabaseConfig(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", 6379),
        db_num=os.environ.get("DB_NUMBER", 0),
    )

    asyncio.run(pipeline(config_db))


if __name__ == "__main__":
    main()
