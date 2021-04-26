"""
Convert our config into supervisord config
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import sys
import argparse

import yaml
from loguru import logger

import src.data_models as dm
from src.config_processor import bridges_to_supervisord


def main():
    """
    Entrypoint of bridge config parser
    """
    log_level = os.getenv("LOGGING_LEVEL")
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    logger.info("Read config file")
    parser = argparse.ArgumentParser(description="Listener process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/bridges.yaml",
    )
    args = parser.parse_args()
    with open(args.config, "r") as file_:
        config_dict = yaml.full_load(file_)
    config = dm.Config(**config_dict)
    supervisord_config = bridges_to_supervisord(config.bridges)

    with open(config.supervisord_config_path, "a") as supervisord_config_file:
        supervisord_config_file.write(supervisord_config)


if __name__ == "__main__":
    main()
