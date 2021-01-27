"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import asyncio
import yaml
import time
import pathlib
import numpy as np  # type: ignore
from PIL import Image  # type: ignore
from numpy import asarray  # type: ignore

sys.path.append("..")

import src.data_models as dm
from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

from src.data_models import MinimalBatchObject, ModelObject

# load the image
image = Image.open("test.jpg")
# convert image to numpy array
data = asarray(image)

model = ModelObject(name="test", address="", stateless=True, batch_size=4)
request_info = dm.RequestInfo(
    input=data,
    parameters={"sound": np.array([255, 1], dtype=np.uint8)},
)
batch = MinimalBatchObject(
    uid="test",
    requests_info=[request_info],
    model=model,
)


async def get_response_batches(receiver):
    res_iterable = receiver.receive()
    async for item in res_iterable:
        sys.stdout.write(str(item))
        image = item.responses_info[0].picture
        im = Image.fromarray(image)
        im.save("result.png")


if __name__ == "__main__":
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "src/utils/data_transfers/zmq-config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.ZMQConfig(**config_dict)

    sender = Sender(
        open_address="tcp://127.0.0.1:5556",
        sync_address="tcp://127.0.0.1:5546",
        config=config,
    )

    receiver = Receiver(
        open_address="tcp://127.0.0.1:5555",
        sync_address="tcp://127.0.0.1:5545",
        config=config,
    )

    sys.stdout.write("Send data\n")
    asyncio.run(sender.send(batch))
    time.sleep(5)
    asyncio.run(get_response_batches(receiver))

    sys.stdout.flush()
