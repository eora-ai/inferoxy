"""
Tests for ContainerRunningChecker with DockerCloudClient
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os

import pytest

import src.data_models as dm
from src.cloud_clients import DockerCloudClient
from src.health_checker.container_running_checker import ContainerRunningChecker, Status

pytestmark = pytest.mark.asyncio


model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=512,
    run_on_gpu=False,
)

config = dm.Config(
    zmq_input_address="",
    zmq_output_address="",
    docker=dm.DockerConfig(
        registry="registry.visionhub.ru",
        login=os.environ.get("DOCKER_LOGIN", ""),
        password=os.environ.get("DOCKER_PASSWORD", ""),
        network=os.environ.get("DOCKER_NETWORK", ""),
    ),
    gpu_all=[1],
    load_analyzer=dm.LoadAnalyzerConfig(
        sleep_time=0.1,
        trigger_pipeline=dm.TriggerPipelineConfig(
            max_model_percent=60
        ),
        running_mean=dm.RunningMeanConfig(
            min_threshold=50,
            max_threshold=100,
            window_size=10
        ),
        stateful_checker=dm.StatefulChecker(
            keep_model=10
        ),
    ),
    health_check=dm.HealthCheckerConfig(
        connection_idle_timeout=10
    ),
    max_running_instances=10,
    models=dm.ModelsRunnerConfig(
        ports=dm.PortConfig(
            sender_open_addr=5566,
            receiver_open_addr=4531,
        ),
        zmq_config=dm.ZMQConfig(sndhwm=123, rcvhwm=121, sndtimeo=123, rcvtimeo=123),
    ),
)


async def test_container_is_running():
    """
    This test is checking that mockcloudclient returns True
    """
    try:
        cloud_client = DockerCloudClient(config)
        model_instance = cloud_client.start_instance(model)
        checker = ContainerRunningChecker(cloud_client)
        status = checker.check(model_instance)
        assert status.is_running
        assert status.reason is None
        assert status.model_instance == model_instance
    finally:
        cloud_client.stop_instance(model_instance)
