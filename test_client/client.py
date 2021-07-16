"""
Test clients for listener
"""

import uuid

import requests

from loguru import logger
import zmq
import numpy as np
from PIL import Image


def main():
    req = requests.post(
        "http://localhost:8000/models",
        json={
            "name": "stub",
            "address": "registry.visionhub.ru/models/stub:v5",
            "stateless": True,
            "batch_size": 128,
            "run_on_gpu": False,
        },
    )
    # logger.info(f"Models loadded {req.json()}")
    context = zmq.Context()

    input_socket = context.socket(zmq.PUSH)
    input_socket.connect("tcp://localhost:7787")
    logger.info("Connected to receiver")
    output_socket = context.socket(zmq.DEALER)
    uid = f"test_{uuid.uuid4()}.png"
    output_socket.setsockopt(zmq.IDENTITY, uid.encode("utf-8"))
    output_socket.connect("tcp://localhost:7788")

    stateless = input("stateless y/n: ") == "y"
    number_of_request = int(input("Number of request: "))

    image = Image.open("test.png")
    image_array = np.asarray(image)

    logger.info("Connected to sender")

    for i in range(number_of_request):

        input_socket.send_pyobj(
            {
                "source_id": uid,
                "model": "stub",
                "inputs": [
                    {
                        "data": image_array,
                        "parameters": {"stateless": stateless, "index": i},
                    }
                ],
            }
        )
        logger.info(f"Sent {i}")

    i = 0
    while i != number_of_request:
        result = output_socket.recv_pyobj()
        if result.get("error", None) is None:
            logger.info(
                f"{i} -> {result['source_id']} -> {result['outputs'][0]['parameters']['index']}"
            )
        else:
            logger.info(f"{i} -> ❌ -> {result.get('error')}")
        i += 1


if __name__ == "__main__":
    main()
