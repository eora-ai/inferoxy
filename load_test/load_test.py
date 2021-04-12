"""
Load tests
"""

import uuid
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch_size",
        type=int,
        help="batch size of models object",
        default=10,
    )
    parser.add_argument(
        "--address",
        type=str,
        help="registry address of model",
        default="registry.visionhub.ru/models/stub:v5",
    )
    parser.add_argument(
        "--stateless",
        type=bool,
        help="stateless of model",
        default=True,
    )
    parser.add_argument(
        "--mode",
        type=int,
        help="Choose mode: 1 - request = batch_size;\
        2 - request = batch_size * 2;\
        3 -request = batch_size * 10 \n",
        default=1,
    )

    # Model params
    args = parser.parse_args()
    address = args.address
    batch_size = int(args.batch_size)
    stateless = bool(args.stateless)
    mode = int(args.mode)

    if mode == 1:
        number_of_request = batch_size
    elif mode == 2:
        number_of_request = batch_size * 2
    elif mode == 3:
        number_of_request = batch_size * 10
    else:
        raise Exception("No such mode")

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
        break

    result.wait()


if __name__ == "__main__":
    main()
