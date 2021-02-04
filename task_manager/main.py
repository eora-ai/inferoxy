"""
Entry point of the task manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import asyncio
import threading
import yaml
from dotenv import load_dotenv

import src.data_models as dm
import src.receiver as rc
import src.sender as snd
from src.batch_processing.queue_processing import send_to_model
from src.load_analyzers import RunningMeanLoadAnalyzer
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.alert_sender import AlertManager
from src.cloud_clients import DockerCloudClient
from src.health_checker.health_checker_pipeline import HealthCheckerPipeline

load_dotenv()


async def pipeline(
    input_batch_queue: InputBatchQueue,
    output_batch_queue: OutputBatchQueue,
    receiver_streams_combiner: ReceiverStreamsCombiner,
    model_instances_storage: ModelInstancesStorage,
    config: dm.Config,
):
    """
    Async pipeline of main IO process, Input is RequestBatches, Output is ResponseBatches
    """
    receiver_socket = rc.create_socket(config)
    receiver_task = rc.receive(receiver_socket, input_batch_queue)
    send_to_model_task = send_to_model(
        input_batch_queue, model_instances_storage=model_instances_storage
    )
    receive_from_model_task = receiver_streams_combiner.converter()
    sender_socket = snd.create_socket(config)
    sender_task = snd.send(sender_socket, output_batch_queue)
    await asyncio.wait(
        [receiver_task, send_to_model_task, receive_from_model_task, sender_task]
    )


def main():
    """
    Entry point
    1. Init internal multithreading queue
    In one thread:
    2. Start reciever
    3. Start processor
    4. Start sender
    In second thread: load analyzer.
    """
    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)
        if os.getenv("CLOUD_CLIENT") == "docker":
            config.docker = dm.DockerConfig(
                registry=os.getenv("DOCKER_REGISTRY"),
                login=os.getenv("DOCKER_LOGIN"),
                password=os.getenv("DOCKER_PASSWORD"),
            )

    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    pipeline_thread = threading.Thread(
        target=asyncio.run,
        args=(
            pipeline(
                input_batch_queue=input_batch_queue,
                output_batch_queue=output_batch_queue,
                receiver_streams_combiner=receiver_streams_combiner,
                model_instances_storage=model_instances_storage,
                config=config,
            ),
        ),
    )
    cloud_client = DockerCloudClient(config)
    load_analyzer_thread = RunningMeanLoadAnalyzer(
        cloud_client,
        input_batch_queue,
        output_batch_queue,
        model_instances_storage=model_instances_storage,
        config=config,
    )
    # TODO: add alert manager
    alert_manager = AlertManager(input_batch_queue, output_batch_queue)
    health_check_thread = HealthCheckerPipeline(
        model_instances_storage, cloud_client, alert_manager, config
    )
    pipeline_thread.start()
    load_analyzer_thread.start()
    health_check_thread.start()

    pipeline_thread.join()
    load_analyzer_thread.join()
    health_check_thread.join()


if __name__ == "__main__":
    main()
