"""
Entry point of the task manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import sys
import asyncio
import logging

import yaml
from loguru import logger

import src.receiver as rc
import src.sender as snd
import src.data_models as dm
from src.alert_sender import AlertManager
from src.cloud_clients import DockerCloudClient
from src.load_analyzers import RunningMeanLoadAnalyzer
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.batch_processing.queue_processing import send_to_model
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.health_checker.health_checker_pipeline import HealthCheckerPipeline


async def pipeline(
    config: dm.Config,
):
    """
    Async pipeline of main IO process, Input is RequestBatches, Output is ResponseBatches
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    cloud_client = DockerCloudClient(config)
    load_analyzer = RunningMeanLoadAnalyzer(
        cloud_client,
        input_batch_queue,
        output_batch_queue,
        model_instances_storage=model_instances_storage,
        config=config,
    )
    alert_manager = AlertManager(
        input_queue=input_batch_queue, output_queue=output_batch_queue
    )
    health_checker = HealthCheckerPipeline(
        model_instances_storage=model_instances_storage,
        cloud_client=cloud_client,
        alert_manager=alert_manager,
        config=config,
    )
    receiver_socket = rc.create_socket(config)
    receiver_task = asyncio.create_task(rc.receive(receiver_socket, input_batch_queue))
    send_to_model_task = asyncio.create_task(
        send_to_model(
            input_batch_queue,
            output_batch_queue,
            model_instances_storage=model_instances_storage,
        )
    )
    receive_from_model_task = asyncio.create_task(receiver_streams_combiner.converter())
    sender_socket = snd.create_socket(config)
    sender_task = asyncio.create_task(snd.send(sender_socket, output_batch_queue))
    health_checker_task = asyncio.create_task(health_checker.pipeline())
    load_analyzer_task = asyncio.create_task(load_analyzer.analyzer_pipeline())

    loop = asyncio.get_event_loop()

    await asyncio.gather(
        receiver_task,
        send_to_model_task,
        receive_from_model_task,
        sender_task,
        load_analyzer_task,
        health_checker_task,
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

    # Set up log level of logger
    log_level = os.getenv("LOGGING_LEVEL")

    logger.remove()
    logger.add(sys.stderr, level=log_level)

    with open("config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config.from_dict(config_dict)
        if os.environ.get("CLOUD_CLIENT") == "docker":
            docker_config_dict = dict(network=os.environ.get("DOCKER_NETWORK"))
            docker_config_dict["registry"] = os.environ.get("DOCKER_REGISTRY")
            docker_config_dict["login"] = os.environ.get("DOCKER_LOGIN")
            docker_config_dict["password"] = os.environ.get("DOCKER_PASSWORD")
            config.docker = dm.DockerConfig(**docker_config_dict)

    logging.getLogger("asyncio").setLevel(logging.DEBUG)
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
