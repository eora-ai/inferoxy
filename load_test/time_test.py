"""
Time test
"""
import uuid
import time
import requests

from loguru import logger
import zmq
import numpy as np
from PIL import Image


def main():
    for i in range(4):
        req = requests.post(
            "http://localhost:8000/models",
            json={
                "name": f"stub_{i}",
                "address": "registry.visionhub.ru/models/stub:v5",
                "stateless": True,
                "batch_size": 128,
                "run_on_gpu": False,
            },
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

    stateless = True

    image = Image.open("test.jpg")
    image_array = np.asarray(image)

    logger.info("Connected to sender")

    for i in range(4):

        input_socket.send_pyobj(
            {
                "source_id": uid,
                "input": image_array,
                "parameters": {"stateless": stateless, "index": 0},
                "model": f"stub_{i}",
            }
        )
    start_time = time.time()

    for i in range(4):
        result = output_socket.recv_pyobj()
        print(result)
        logger.info(
            f"{i} -> {result['uid']} -> {result['response_info']['parameters']['index']}"
        )
    end_time = time.time() - start_time
    logger.info(f"Processing and sending response took {end_time}")


if __name__ == "__main__":
    main()
