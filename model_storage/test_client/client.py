"""
This is test client for model storage
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys

import zmq  # type: ignore
from loguru import logger
from envyaml import EnvYAML     # type: ignore

sys.path.append("..")

import src.data_models as dm    # type: ignore


def update_config(config, config_path):
    env = EnvYAML(config_path, strict=False)
    config.address = env["address"]

    database = dm.DatabaseConfig.parse_obj(env["database"])
    config.database = database

    return config


def main():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REQ)
    config_path_env = "../config_env.yaml"
    config = dm.Config.parse_file("../config.yaml", content_type="yaml")

    config = update_config(config, config_path_env)

    sock.connect(config.address)

    model_slug = "stub"

    logger.info("Send model slug")
    sock.send_string(model_slug)
    logger.info("Start listening")
    result = sock.recv_pyobj()
    logger.info(f"Model object {result}")


if __name__ == "__main__":
    main()
