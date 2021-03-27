"""
Load tests
"""

import uuid

import requests
from functools import partial
from multiprocessing.pool import ThreadPool

import docker
from loguru import logger
import zmq
import numpy as np
from PIL import Image


def send_request(obj, inp_sock):
    inp_sock.send_pyobj(obj)


def receive_response(out_sock):
    out_sock.recv_pyobj()


def main():
    mode = int(input("Choose mode: 1 - request = batch_size;\
                     2 - request = batch_size * 2;\
                     3 -request = batch_size * 10 \n"))

    # Model params

    batch_size = int(input("Batch size of model: "))

    stateless = True

    if mode == 1:
        number_of_request = batch_size
    elif mode == 2:
        number_of_request = batch_size * 2
    elif mode == 3:
        number_of_request = batch_size * 10
    else:
        raise Exception("")

    address = "registry.visionhub.ru/models/stub:v5"

    req = requests.post(
        "http://localhost:8000/models",
        json={
            "name": "stub",
            "address": address,
            "stateless": True,
            "batch_size": batch_size,
            "run_on_gpu": False,
        },
    )
    logger.info(f"Models loadded {req.json()}")

    # Set up connection with inferoxy

    context = zmq.Context()

    input_socket = context.socket(zmq.PUSH)
    input_socket.connect("tcp://localhost:7787")
    logger.info("Connected to receiver")
    output_socket = context.socket(zmq.DEALER)
    uid = f"test_{uuid.uuid4()}.jpg"
    output_socket.setsockopt(zmq.IDENTITY, uid.encode("utf-8"))
    output_socket.connect("tcp://localhost:7788")

    image = Image.open("test.jpg")
    image_array = np.asarray(image)

    logger.info("Connected to sender")

    # Build requests
    requests_data = []
    for i in range(number_of_request):
        data = {
            "source_id": uid,
            "input": image_array,
            "parameters": {"stateless": stateless, "index": i},
            "model": "stub",
        }
        requests_data.append(data)

    # Send data in multithreading
    p = ThreadPool(300)
    prod_send = partial(send_request, inp_sock=input_socket)
    result = p.map_async(prod_send, requests_data)

    while True:
        receive_response(output_socket)

        client = docker.from_env()
        containers = client.containers.list()

        logger.info(containers)

        times = 0
        for container in containers:
            logger.info(container.image)
            if container.image == client.images.get(address):
                times += 1

        logger.info(f"Containers number: {times}")

    result.wait()


if __name__ == "__main__":
    main()
