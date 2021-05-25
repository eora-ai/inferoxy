"""
Tests for health checker pipeline
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os

import pytest

import src.data_models as dm
from src.batch_queue import OutputBatchQueue
from src.health_checker.checker import Status
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from src.model_instances_storage import ModelInstancesStorage
from src.cloud_clients.mock_cloud_client import MockCloudClient
from src.alert_sender.mock_alert_manager import MockAlertManager
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.health_checker.health_checker_pipeline import HealthCheckerPipeline
from src.health_checker.errors import ContainerExited, ContainerDoesNotExists


config = dm.Config(
    zmq_input_address="",
    zmq_output_address="",
    cloud_client=dm.DockerConfig(
        registry="registry.visionhub.ru",
        login=os.environ.get("DOCKER_LOGIN", ""),
        password=os.environ.get("DOCKER_PASSWORD", ""),
        network=os.environ.get("DOCKER_NETWORK", ""),
    ),
    gpu_all=[1],
    load_analyzer=dm.LoadAnalyzerConfig(
        sleep_time=0.1,
        trigger_pipeline=dm.TriggerPipelineConfig(max_model_percent=60),
        running_mean=dm.RunningMeanConfig(
            min_threshold=50, max_threshold=100, window_size=10
        ),
        stateful_checker=dm.StatefulChecker(keep_model=10),
    ),
    health_check=dm.HealthCheckerConfig(connection_idle_timeout=10),
    max_running_instances=10,
    models=dm.ModelsRunnerConfig(
        ports=dm.PortConfig(
            sender_open_addr=5566,
            receiver_open_addr=4531,
        ),
        zmq_config=dm.ZMQConfig(sndhwm=123, rcvhwm=121, sndtimeo=123, rcvtimeo=123),
    ),
)

model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=512,
    run_on_gpu=False,
)
model_instance1 = dm.ModelInstance(
    model=model,
    name="Test",
    sender=BaseSender(),
    receiver=BaseReceiver(),
    lock=True,
    hostname="",
    source_id="",
    running=True,
)
model_instance2 = dm.ModelInstance(
    model=model,
    name="Test2",
    sender=BaseSender(),
    receiver=BaseReceiver(),
    lock=True,
    hostname="",
    source_id="",
    running=True,
)
model_instance3 = dm.ModelInstance(
    model=model,
    name="Test3",
    sender=BaseSender(),
    receiver=BaseReceiver(),
    lock=True,
    hostname="",
    source_id="",
    running=True,
)

pytestmark = pytest.mark.asyncio


async def test_make_decision():
    """
    This test for HealthCheckerPipeline.make_decision
    """

    output_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)
    model_instances_storage.add_model_instance(model_instance3)
    mock_cloud_client = MockCloudClient(20, config)
    alert_manager = MockAlertManager()

    health_checker_pipeline = HealthCheckerPipeline(
        model_instances_storage, mock_cloud_client, alert_manager, config
    )

    retriable_error = ContainerDoesNotExists("Container doesnot exists")
    failed_error = ContainerExited("Container exited")

    statuses = [
        Status(model_instance=model_instance1, is_running=True),
        Status(
            model_instance=model_instance2, is_running=False, reason=retriable_error
        ),
        Status(model_instance=model_instance3, is_running=False, reason=failed_error),
    ]

    await health_checker_pipeline.make_decision(statuses)

    assert alert_manager.get_errors() == {model_instance3: failed_error}
