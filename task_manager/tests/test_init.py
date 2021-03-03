"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import asyncio

import cv2  # type: ignore
import yaml
import pydub  # type: ignore
import pathlib
import numpy as np  # type: ignore
from PIL import Image  # type: ignore

from numpy import asarray  # type: ignore
from moviepy.editor import VideoFileClip  # type: ignore

sys.path.append("..")

import src.data_models as dm
from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver
from shared_modules.utils import uuid4_string_generator
from src.data_models import MinimalBatchObject, ModelObject

stub_model = model = ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=256,
)


async def get_response_batches(receiver):
    print("Enter get response batches")
    response_iterable = receiver.receive()
    print("Receive response iterable")
    async for item in response_iterable:
        print(np.nonzero(item.responses_info[0].parameters["sound"]))
        for info in item.responses_info:
            image = info.picture
            im = Image.fromarray(image)
            # im.save("result.png")
            sound = info.parameters["sound"]


def build_batch_video():
    movie = VideoFileClip("test.mp4")
    vcap = cv2.VideoCapture("test.mp4")

    if vcap.isOpened():
        # get vcap property
        width = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))

    uid_generator = uuid4_string_generator()
    audio = movie.audio
    count_img = 0
    audio_array = audio.to_soundarray()
    for frame in movie.iter_frames():
        count_img += 1
    sound_per_frame = len(audio_array) // count_img
    requests_info = []
    sound = audio_array[:sound_per_frame]
    request_info_first = dm.RequestInfo(
        input=next(movie.iter_frames()),
        parameters={
            "sound": sound,
            "init": {
                "height": height,
                "width": width,
                "fps": int(fps),
                "length": frame_count,
            },
        },
    )
    requests_info.append(request_info_first)

    for i, item in enumerate(movie.iter_frames()):
        if i == 0:
            pass
        else:
            sound = audio_array[
                i * sound_per_frame : (i * sound_per_frame + sound_per_frame)
            ]
            if not [] in sound:
                request_info = dm.RequestInfo(
                    input=frame,
                    parameters={
                        "sound": sound,
                    },
                )
                requests_info.append(request_info)

    batch = MinimalBatchObject(
        uid=next(uid_generator),
        requests_info=requests_info,
        model=stub_model,
    )
    return batch


def build_batch_picture():
    # load the image
    image = Image.open("test.jpg")
    sound = np.asarray(
        pydub.AudioSegment.from_mp3("test.mp3").get_array_of_samples(), dtype=np.int64
    )

    width, height = image.size
    # convert image to numpy array
    data = asarray(image)

    request_info = dm.RequestInfo(
        input=data,
        parameters={
            "sound": sound,
            "init": {"height": height, "width": width, "fps": 1, "length": 1},
        },
    )

    batch = MinimalBatchObject(
        uid="test",
        requests_info=[request_info],
        model=model,
    )
    return batch


async def main():
    cur_path = pathlib.Path(__file__)
    config_path = cur_path.parent.parent / "config.yaml"

    with open(config_path) as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)

    batch = build_batch_video()
    print(batch.requests_info[0].parameters)
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
    print("Send data\n")
    await sender.send(batch)
    await get_response_batches(receiver)


if __name__ == "__main__":
    asyncio.run(main())
