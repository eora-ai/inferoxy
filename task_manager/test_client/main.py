"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import yaml
import zmq
import time
import pathlib
import asyncio
from PIL import Image  # type: ignore
from numpy import asarray  # type: ignore
from loguru import logger

sys.path.append("..")

import src.data_models as dm
import src.receiver as rcv

from src.data_models import MinimalBatchObject, ModelObject
from src.batch_queue import InputBatchQueue


stub_model = model = ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=256,
)

#  load the image
image = Image.open("test.jpg")
# convert image to numpy array
data = asarray(image)

request_info = dm.RequestInfo(
    input=data,
    parameters={},
)
batch = MinimalBatchObject(
    uid="test",
    requests_info=[request_info],
    model=stub_model,
)
input_queue = InputBatchQueue()


async def get_response_batches(receiver):
    res_iterable = receiver.receive()
    async for item in res_iterable:
        sys.stdout.write(str(item))
        image = item.responses_info[0].picture
        im = Image.fromarray(image)
        im.save("result.png")


def main():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUB)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = rcv.create_socket(config)

    sock_sender.send_pyobj(batch)
    asyncio.run(rcv.receive(sock_receiver, input_queue))

    logger.info("Receive data")


if __name__ == "__main__":
    main()
