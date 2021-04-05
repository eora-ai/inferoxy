"""
Entry point of the task manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path

from loguru import logger
from envyaml import EnvYAML     # type: ignore

import src.receiver as rc
import src.sender as snd
import src.data_models as dm
from src.alert_sender import AlertManager
from src.cloud_clients import DockerCloudClient, KubeCloudClient, BaseCloudClient
from src.load_analyzers import RunningMeanLoadAnalyzer
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.batch_processing.queue_processing import send_to_model
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.health_checker.health_checker_pipeline import HealthCheckerPipeline
from shared_modules.parse_config import build_config_file


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

    if not config.docker is None:
        cloud_client: BaseCloudClient = DockerCloudClient(config)
    elif not config.kube is None:
        cloud_client = KubeCloudClient(config)
    else:
        raise ValueError("Cloud client must be selected")

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

    await asyncio.gather(
        receiver_task,
        send_to_model_task,
        receive_from_model_task,
        sender_task,
        load_analyzer_task,
        health_checker_task,
    )


def update_config(config, config_path):
    env = EnvYAML(config_path, strict=False)
    if "$" in env['kube']['address']:
        config.kube = None
        config.docker = dm.DockerConfig.parse_obj(env['docker'])
    else:
        config.docker = None
        config.kube = dm.KubeConfig.parse_obj(env['kube'])
    config.gpu_all = env['gpu_all']

    health_check = dm.HealthCheckerConfig.parse_obj(env['health_check'])
    config.health_check = health_check

    load_analyzer = dm.LoadAnalyzerConfig.parse_obj(env['load_analyzer'])
    config.load_analyzer = load_analyzer

    config.max_running_instances = env['max_running_instances']

    models = dm.ModelsRunnerConfig.parse_obj(env['models'])
    config.models = models

    config.zmq_input_address = env['zmq_input_address']

    config.zmq_output_address = env['zmq_output_address']

    return config


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

    parser = argparse.ArgumentParser(description="Task manager process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/task_manager.yaml",
    )
    args = parser.parse_args()
    print(args.config)

    config = dm.Config.parse_file(args.config, content_type="yaml")

    env_config_path = build_config_file(config, args.config, "task_manager")

    config = update_config(config, env_config_path)

    Path(config.zmq_output_address).parent.mkdir(parents=True, exist_ok=True)

    logging.getLogger("asyncio").setLevel(logging.DEBUG)
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
