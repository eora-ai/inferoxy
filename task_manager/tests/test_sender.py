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
    parameters={},
)
batch = MinimalBatchObject(
    uid="test",
    requests_info=[request_info],
    model=model,
)

cur_path = pathlib.Path(__file__)
config_path = cur_path.parent / "config.yaml"

with open(config_path) as config_file:
    config_dict = yaml.full_load(config_file)
    config = dm.Config.from_dict(config_dict)


async def get_response_batches(receiver):
    res_iterable = receiver.receive()
    async for item in res_iterable:
        sys.stdout.write(str(item))


if __name__ == "__main__":

    sender = Sender(
        open_address="tcp://127.0.0.1:5556",
        sync_address="tcp://127.0.0.1:5546",
        config=config.models.zmq_config,
    )

    receiver = Receiver(
        open_address="tcp://127.0.0.1:5555",
        sync_address="tcp://127.0.0.1:5545",
        config=config.models.zmq_config,
    )

    sys.stdout.write("Send data\n")
    asyncio.run(sender.send(batch))
    time.sleep(5)
    asyncio.run(get_response_batches(receiver))

    sys.stdout.flush()
