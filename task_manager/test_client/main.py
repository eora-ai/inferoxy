"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import os
import yaml
import zmq
import pathlib
import numpy as np

from moviepy.editor import VideoFileClip
from PIL import Image  # type: ignore
from loguru import logger

sys.path.append("..")

import src.data_models as dm

from src.data_models import MinimalBatchObject, ModelObject
from shared_modules.utils import uuid4_string_generator


stub_model = model = ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=256,
)


def extract_frames_at_times(movie, times, imgdir):
    clip = VideoFileClip(movie)
    for t in times:
        imgpath = os.path.join(imgdir, "{}.png".format(t))
        clip.save_frame(imgpath, t)
        #  load the image
        image = Image.open(imgpath)

        # convert image to numpy array
        data = np.asarray(image)
        yield data


def batch_video():
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

    movie = VideoFileClip("without_sound_cutted.mp4")
    uid_generator = uuid4_string_generator()
    for frame in movie.iter_frames():
        request_info = dm.RequestInfo(
            input=frame,
            parameters={},
        )
        batch = MinimalBatchObject(
            uid=next(uid_generator),
            requests_info=[request_info],
            model=stub_model,
        )
        print(batch)
        sock_sender.send_pyobj(batch)
    logger.info("Start listening")
    while True:
        result = sock_receiver.recv_pyobj()
        logger.info(f"Result batch {result}")


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
    data = np.asarray(image)

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
