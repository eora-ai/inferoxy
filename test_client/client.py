"""
Test clients for listener
"""

from loguru import logger
import zmq
import numpy as np
from PIL import Image


def main():
    context = zmq.Context()

    input_socket = context.socket(zmq.PUSH)
    input_socket.connect("tcp://localhost:7787")
    logger.info("Connected to receiver")
    output_socket = context.socket(zmq.SUB)
    output_socket.connect("tcp://localhost:7788")

    stateless = input("y/n: ") == "y"
    number_of_request = int(input("Number of request: "))

    image = Image.open("test.jpg")
    image_array = np.asarray(image)

    output_socket.subscribe(b"test.jpg")
    logger.info("Connected to sender")

    for i in range(number_of_request):

        input_socket.send_pyobj(
            {
                "source_id": "test.jpg",
                "input": image_array,
                "parameters": {"stateless": stateless},
                "model": "stub",
            }
        )
        logger.info(f"Sent {i}")

    for i in range(number_of_request):
        topic = output_socket.recv_string()
        result = output_socket.recv_pyobj()
        logger.info(f"{topic} -> {result['uid']} -> {i}")


if __name__ == "__main__":
    main()
