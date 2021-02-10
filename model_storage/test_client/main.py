"""
This is test client for model storage
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys
import zmq
import yaml

from loguru import logger

sys.path.append("..")

import src.data_models as dm


def main():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REQ)
    with open("../config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)

    sock.connect(config_dict["address"])

    model_slug = "stub"

    logger.info("Send model slug")
    sock.send_string(model_slug)
    logger.info("Start listening")
    result = sock.recv_pyobj()
    logger.info(f"Model object {result}")


if __name__ == "__main__":
    main()
