"""
Test clients for listener
"""

import time
import sys

from loguru import logger
import zmq  # type: ignore
import numpy as np  # type: ignore
from PIL import Image  # type: ignore

sys.path.append("..")

import src.data_models as dm


def main():
    context = zmq.Context()
    batch_manager_input_socket = context.socket(zmq.PULL)
    batch_manager_input_socket.bind("ipc:///tmp/batch_manager/input")
    batch_manager_input_socket.subscribe(b"")
    debatch_manager_output_socket = context.socket(zmq.PUSH)
    debatch_manager_output_socket.bind("ipc:///tmp/debatch_manager/result")
    time.sleep(5)
    image = Image.open("test.jpg")
    image_array = np.asarray(image)
    input_socket = context.socket(zmq.PUB)
    input_socket.connect("tcp://localhost:7787")
    output_socket = context.socket(zmq.SUB)
    output_socket.connect("tcp://localhost:7788")
    output_socket.subscribe(b"")

    input_socket.send_pyobj(
        {
            "source_id": "test.jpg",
            "input": image_array,
            "parameters": {},
            "model": "stub",
        }
    )

    input_request_object: dm.RequestObject = batch_manager_input_socket.recv_pyobj()
    logger.info(input_request_object)
    response = dm.ResponseObject(
        uid=input_request_object.uid,
        source_id=input_request_object.source_id,
        model=input_request_object.model,
        response_info=None,
        error="Test",
    )
    debatch_manager_output_socket.send_pyobj(response)
    result = output_socket.recv_pyobj()
    logger.info(result)


if __name__ == "__main__":
    main()
