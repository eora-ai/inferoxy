"""
Test sender from backend
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import asyncio
import pathlib
from typing import List

import cv2  # type: ignore
import yaml
import zmq.asyncio  # type: ignore
import numpy as np  # type: ignore
from PIL import Image  # type: ignore
from numpy import asarray  # type: ignore

# from scipy.io.wavfile import write  # type: ignore
from moviepy.editor import VideoFileClip  # type: ignore
from moviepy.audio.AudioClip import AudioArrayClip  # type: ignore

sys.path.append("..")

import src.data_models as dm
from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver
from shared_modules.utils import uuid4_string_generator
from src.data_models import MinimalBatchObject, ModelObject
from src.batch_queue import OutputBatchQueue
from src.receiver_streams_combiner import ReceiverStreamsCombiner


stub_model = model = ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v5",
    stateless=True,
    batch_size=256,
)

context = zmq.asyncio.Context()
response_batches: List[dm.ResponseBatch] = []


def join_clips_with_audio(source_video, sound_frames, audio_fps, result_path):
    clip = VideoFileClip(source_video)
    if sound_frames is not None:
        sound_frames = np.array(sound_frames)
        audio = AudioArrayClip(sound_frames, fps=audio_fps)
        clip = clip.set_audio(audio)
        clip.write_videofile(result_path, codec="libx264", audio_codec="aac")


async def get_response_batches_video(receiver_streams):
    print("Enter get response batches")
    done, _ = await asyncio.wait(
        (
            receiver_streams.converter(),
            get_from_queue(receiver_streams.output_batch_queue),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    for batch in response_batches:
        print("Receive response iterable")
        images = []
        audio = []
        fps = batch.responses_info[0].parameters["init"]["fps"]

        for info in batch.responses_info:
            print("Processing response info of batch")
            image = info.picture
            images.append(image)

            height, width, layers = image.shape
            size = (width, height)
            sound = info.parameters["sound"]

            audio.extend(sound)

    print("Create videofile")
    out = cv2.VideoWriter(
        "result_without_sound.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, size
    )
    for i in range(len(images)):
        out.write(images[i])
    out.release()

    audio = np.array(audio, dtype=np.float32)
    print("Video file without is created")
    # scaled = np.int16(audio / np.max(np.abs(audio)) * 32767)

    join_clips_with_audio(
        "result_without_sound.mp4", audio, 44100, "result_with_sound.mp4"
    )


async def get_from_queue(output_batch_queue):
    response_batch = await output_batch_queue.get()
    print(response_batch)
    response_batches.append(response_batch)


async def get_response_batches_picture(receiver_streams):
    print("Enter get response batches")
    done, _ = await asyncio.wait(
        (
            receiver_streams.converter(),
            get_from_queue(receiver_streams.output_batch_queue),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    print("Receive response iterable")

    print(response_batches)
    for batch in response_batches:
        for info in batch.responses_info:
            image = info.picture
            im = Image.fromarray(image)
            im.save("result.png")


def build_batch_video():
    movie = VideoFileClip("test.mp4")
    vcap = cv2.VideoCapture("test.mp4")

    if vcap.isOpened():
        # get vcap property
        width = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        height = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        fps = vcap.get(cv2.CAP_PROP_FPS)
        frame_count = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Number of frames in video {frame_count}")

    uid_generator = uuid4_string_generator()

    audio = movie.audio
    # count_img = 0
    audio_array = audio.to_soundarray()

    sound_per_frame = len(audio_array) // frame_count
    requests_info = []
    sound = audio_array[:sound_per_frame]

    iterator = movie.iter_frames()

    request_info_first = dm.RequestInfo(
        input=next(iterator),
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

    for i, frame in enumerate(iterator):
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

    width, height = image.size
    # convert image to numpy array
    data = asarray(image)

    request_info = dm.RequestInfo(
        input=data,
        parameters={},
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

    config = dm.Config.parse_file(config_path, content_type="yaml")

    print("What you want to process? Press 1 - picture; 2 - video")
    choice = int(input())

    if choice == 1:
        batch = build_batch_picture()
    if choice == 2:
        batch = build_batch_video()
    sender = Sender(
        open_address="tcp://127.0.0.1:5556",
        config=config.models.zmq_config,
        context=context,
    )

    receiver = Receiver(
        open_address="tcp://127.0.0.1:5555",
        config=config.models.zmq_config,
        context=context,
    )
    model_instance = dm.ModelInstance(
        model=stub_model,
        source_id="test.jpg",
        sender=sender,
        receiver=receiver,
        lock=False,
        hostname="stub_v1",
        running=True,
        name="stub-v1",
    )
    receiver.set_model_instance(model_instance)
    output_batch_queue = OutputBatchQueue()
    receiver_streams = ReceiverStreamsCombiner(output_batch_queue)
    receiver_streams.add_listener(receiver)

    print("Send data\n")
    await sender.send(batch)
    if choice == 1:
        await get_response_batches_picture(receiver_streams)
    if choice == 2:
        await get_response_batches_video(receiver_streams)


if __name__ == "__main__":
    asyncio.run(main())
