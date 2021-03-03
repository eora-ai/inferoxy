"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import pathlib

import zmq  # type: ignore
import yaml  # type: ignore
import numpy as np  # type: ignore
from PIL import Image  # type: ignore
from loguru import logger
from moviepy.editor import VideoFileClip  # type: ignore

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


def batches_different_sources():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUSH)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.PULL)
    sock_receiver.bind(config.zmq_output_address)
    movie = VideoFileClip("without_sound_cutted.mp4")
    uid_generator = uuid4_string_generator()

    requests_info1 = []
    requests_info2 = []
    frames = []
    for item in movie.iter_frames():
        frames.append(item)

    for frame in frames[: len(frames) // 2]:
        request_info = dm.RequestInfo(
            input=frame,
            parameters={},
        )
        requests_info1.append(request_info)

    for frame in frames[len(frames) // 2 :]:
        request_info = dm.RequestInfo(
            input=frame,
            parameters={},
        )
        requests_info2.append(request_info)

    batch1 = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info1,
        model=stub_model,
        source_id="source_id1",
    )

    batch2 = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info2,
        model=stub_model,
        source_id="source_id1",
    )

    batch3 = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info1,
        model=stub_model,
        source_id="source_id2",
    )

    batch4 = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info2,
        model=stub_model,
        source_id="source_id2",
    )
    batches = [batch1, batch2, batch3, batch4]
    for batch in batches:
        print(batch)
        sock_sender.send_pyobj(batch)

    logger.info("Start Listening")
    while True:
        result = sock_receiver.recv_pyobj()
        logger.info(f"Result batch {result}")


def batches_video_with_sound():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUSH)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.PULL)
    sock_receiver.bind(config.zmq_output_address)

    movie = VideoFileClip("cat_with_sound.mp4")
    uid_generator = uuid4_string_generator()
    audio = movie.audio
    count_img = 0
    audio_array = audio.to_soundarray()
    for frame in movie.iter_frames():
        count_img += 1
    sound_per_frame = len(audio_array) // count_img
    requests_info = []
    for i in range(count_img):
        sound = audio_array[
            i * sound_per_frame : (i * sound_per_frame + sound_per_frame) : 1
        ]
        if not [] in sound:
            request_info = dm.RequestInfo(
                input=frame,
                parameters={"sound": sound},
            )
            requests_info.append(request_info)

    batch = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info,
        model=stub_model,
    )
    sock_sender.send_pyobj(batch)
    logger.info("Start Listening")
    while True:
        result = sock_receiver.recv_pyobj()
        logger.info(f"Result batch {result}")


def batches_video_without_sound():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUSH)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.PULL)
    sock_receiver.bind(config.zmq_output_address)

    movie = VideoFileClip("without_sound_cutted.mp4")
    uid_generator = uuid4_string_generator()
    requests_info = []
    for frame in movie.iter_frames():
        request_info = dm.RequestInfo(
            input=frame,
            parameters={},
        )
        requests_info.append(request_info)

    batch = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info,
        model=stub_model,
    )
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
    sock_sender = ctx.socket(zmq.PUSH)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.PULL)
    sock_receiver.bind(config.zmq_output_address)

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
    batch_pictures()
