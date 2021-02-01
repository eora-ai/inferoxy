"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import yaml
import zmq
import pathlib

from moviepy.editor import VideoFileClip
from PIL import Image  # type: ignore
from numpy import asarray  # type: ignore
from loguru import logger

sys.path.append("..")

import src.data_models as dm

from src.data_models import MinimalBatchObject, ModelObject


stub_model = model = ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=256,
)


def batch_video():
    video = VideoFileClip("without_sound_cutted.mp4")
    print([frame for frame in video.iter_frames()])


def batch_pictures():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUB)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.SUB)
    sock_receiver.bind(config.zmq_output_address)
    sock_receiver.subscribe(b"")

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
    sock_sender.send_pyobj(batch)
    logger.info("Start listening")

    while True:
        result = sock_receiver.recv_pyobj()
        logger.info(f"Result batch {result}")


if __name__ == "__main__":
    batch_video()
