"""
Test clients for listener
"""

import uuid

from loguru import logger
import zmq
import numpy as np
from PIL import Image


def main():
    context = zmq.Context()

    input_socket = context.socket(zmq.PUSH)
    input_socket.connect("tcp://localhost:7787")
    logger.info("Connected to receiver")
    output_socket = context.socket(zmq.DEALER)
    uid = f"test_{uuid.uuid4()}.jpg"
    output_socket.setsockopt(zmq.IDENTITY, uid.encode("utf-8"))
    output_socket.connect("tcp://localhost:7788")

    stateless = input("y/n: ") == "y"
    number_of_request = int(input("Number of request: "))

    image = Image.open("test.jpg")
    image_array = np.asarray(image)

    logger.info("Connected to sender")

    for i in range(number_of_request):

        input_socket.send_pyobj(
            {
                "source_id": uid,
                "input": image_array,
                "parameters": {"stateless": stateless, "index": i},
                "model": "stub",
            }
        )
        logger.info(f"Sent {i}")

    for i in range(number_of_request):
        result = output_socket.recv_pyobj()
        logger.info(
            f"{i} -> {result['uid']} -> {result['response_info']['parameters']['index']}"
        )


if __name__ == "__main__":
    main()
