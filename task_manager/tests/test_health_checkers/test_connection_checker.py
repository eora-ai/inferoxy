"""
Tests for connection checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import time

import pytest

import src.data_models as dm
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from src.cloud_clients.mock_cloud_client import MockCloudClient
from src.health_checker.connection_stable_checker import ConnectionChecker, Status


model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=512,
    run_on_gpu=False,
)

pytestmark = pytest.mark.asyncio

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


async def test_was_received_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        name="",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None), config=config)
    result = checker.check(model_instance)
    assert result == Status(model_instance, True)


async def test_wasnot_received_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        name="",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None), config=config)
    model_instance.receiver.last_received_batch = time.time() - 100
    result = checker.check(model_instance)
    assert result == Status(model_instance, True)


async def test_wasnot_received_sent_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        name="",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None), config=config)
    model_instance.receiver.last_received_batch = time.time() - 100
    model_instance.sender.last_sent_batch = time.time() - 100
    result = checker.check(model_instance)
    assert result.reason.code == "E011"


async def test_model_doesnot_locked():
    model_instance = dm.ModelInstance(
        model=model,
        name="",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None))
    model_instance.receiver.last_received_batch = time.time() - 100
    model_instance.sender.last_sent_batch = time.time() - 100
    result = checker.check(model_instance)
    assert result == Status(model_instance, True)
