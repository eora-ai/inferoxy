"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import asyncio
import numpy as np  # type: ignore
import time
from PIL import Image
from numpy import asarray

sys.path.append("..")

from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

from src.data_models import MinimalBatchObject, ModelObject
import src.utils.data_transfers.settings as settings

# load the image
image = Image.open("test.jpg")
# convert image to numpy array
data = asarray(image)

model = ModelObject(name="test", address="", stateless=True, batch_size=4)
batch = MinimalBatchObject(
    uid="test",
    inputs=[data],
    parameters=[],
    model=model,
)

if __name__ == "__main__":
    sender = Sender(
        open_address="tcp://127.0.0.1:5556",
        sync_address="tcp://127.0.0.1:5546",
        settings=settings,
    )

    receiver = Receiver(
        open_address="tcp://127.0.0.1:5555",
        sync_address="tcp://127.0.0.1:5545",
        settings=settings,
    )

    sys.stdout.write("Send data\n")
    data = {"batch_object": batch}
    asyncio.run(sender.send(data))
    time.sleep(5)
    res = asyncio.run(receiver.receive())
    sys.stdout.write(str(res))
    sys.stdout.flush()
