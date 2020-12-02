"""
Entry point of the task manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
import threading
import yaml

import src.data_models as dm
import src.receiver as rc
import src.sender as snd
from src.batch_processing.queue_processing import send_to_model
from src.load_analyzer import RunningMeanLoadAnalyzer
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.response_to_batch import ResponseToBatch
from src.cloud_client import DockerCloudClient


async def pipeline(
    input_batch_queue: InputBatchQueue,
    output_batch_queue: OutputBatchQueue,
    config: dm.Config,
):
    """
    Async pipeline of main IO process, Input is RequestBatches, Output is ResponseBatches
    """
    receiver_socket = rc.create_socket(config)
    receiver_task = rc.receive(receiver_socket, input_batch_queue)
    response_to_batch_converter = ResponseToBatch(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(response_to_batch_converter)
    send_to_model_task = send_to_model(
        input_batch_queue, model_instances_storage=model_instances_storage
    )
    receive_from_model_task = response_to_batch_converter.converter()
    sender_socket = snd.create_socket(config)
    sender_task = snd.send(sender_socket, output_batch_queue)
    await asyncio.wait(
        [receiver_task, send_to_model_task, receive_from_model_task, sender_task]
    )


def main():
    """
    Entry point
    1. Init internal multithreading queue
    In one thread
    2. Start reciever
    3. Start processor
    4. Start sender
    In secodn thread load analyzer.
    """
    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    pipeline_thread = threading.Thread(
        target=asyncio.run,
        args=(
            pipeline(
                input_batch_queue=input_batch_queue,
                output_batch_queue=output_batch_queue,
                config=config,
            ),
        ),
    )
    cloud_client = DockerCloudClient(config)
    load_analyzer_thread = RunningMeanLoadAnalyzer(
        cloud_client, input_batch_queue, output_batch_queue
    )
    pipeline_thread.start()
    load_analyzer_thread.start()

    pipeline_thread.join()
    load_analyzer_thread.join()


if __name__ == "__main__":
    main()
