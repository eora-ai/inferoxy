"""
Entrypoint of listener component
"""

import os
import sys
import argparse

import yaml
from loguru import logger

from src.adapters.python_zeromq_adapter import ZMQPythonAdapter
import src.data_models as dm


def main():
    log_level = os.getenv("LOGGING_LEVEL")
    logger.remove()
    logger.add(sys.stderr, level=log_level)

    logger.info("Read config file")
    parser = argparse.ArgumentParser(description="Listener process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/listener.yaml",
    )
    args = parser.parse_args()

    with open(args.config) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    adapter = ZMQPythonAdapter(config)
    logger.info("Listener started")
    adapter.start()


if __name__ == "__main__":
    main()
