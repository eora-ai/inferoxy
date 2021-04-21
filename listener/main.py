"""
Entrypoint of listener component
"""

import os
import sys
import argparse

from loguru import logger

from shared_modules.parse_config import read_config_with_env
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

    config = read_config_with_env(dm.Config, args.config, "listener")

    adapter = ZMQPythonAdapter(config)
    logger.info("Listener started")
    adapter.start()


if __name__ == "__main__":
    main()
