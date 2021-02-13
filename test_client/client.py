"""
Test clients for listener
"""

import time
import sys

from loguru import logger
import zmq
import numpy as np
from PIL import Image

import shared_modules.data_objects as dm


def main():
    context = zmq.Context()
    image = Image.open("test.jpg")
    image_array = np.asarray(image)
    input_socket = context.socket(zmq.PUSH)
    input_socket.connect("tcp://localhost:7787")
    logger.info("Connected to receiver")
    output_socket = context.socket(zmq.PULL)
    output_socket.connect("tcp://localhost:7788")
    logger.info("Connected to sender")

    input_socket.send_pyobj(
        {
            "source_id": "test.jpg",
            "input": image_array,
            "parameters": {},
            "model": "stub",
        }
    )
    logger.info("Sent")

    result = output_socket.recv_pyobj()
    logger.info(result)


if __name__ == "__main__":
    main()
