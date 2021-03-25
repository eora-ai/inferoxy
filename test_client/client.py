"""
Test clients for listener
"""

import uuid

import requests
import yaml

from loguru import logger
import zmq
import numpy as np
from PIL import Image


def main():
    with open("/etc/inferoxy/models.yaml", "w") as file_:
        yaml.dump(
            {
                "test": {
                    "address": "public.registry.visionhub.ru/models/test:v4",
                    "stateless": True,
                    "batch_size": 128,
                    "run_on_gpu": False,
                }
            },
            file_,
        )
        req = requests.put(
            "http://localhost:8000/models",
            json=[
                {
                    "name": "stub",
                    "address": "registry.visionhub.ru/models/stub:v4",
                    "stateless": True,
                    "batch_size": 128,
                    "run_on_gpu": False,
                }
            ],
        )
    logger.info(f"Models loadded {req.json()}")
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
                "model": "test",
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
