"""
Entrypoint of grpc bridge
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import os
import sys
import argparse

from loguru import logger

from grpcalchemy.config import DefaultConfig

from shared_modules.parse_config import read_config_with_env
from src.services import get_inference_service
import src.data_models as dm


if __name__ == "__main__":
    # Set up log level of logger
    log_level = os.getenv("LOGGING_LEVEL")

    logger.remove()
    logger.add(sys.stderr, level=log_level)

    parser = argparse.ArgumentParser(description="Task manager process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/grpc_bridge.yaml",
    )
    args = parser.parse_args()
    config: dm.Config = read_config_with_env(dm.Config, args.config, "grpc_bridge")
    default_config = DefaultConfig()
    default_config.GRPC_SERVER_HOST = config.host
    default_config.GRPC_SERVER_PORT = config.port
    inference_service = get_inference_service(config)
    inference_service.run(config=default_config)
