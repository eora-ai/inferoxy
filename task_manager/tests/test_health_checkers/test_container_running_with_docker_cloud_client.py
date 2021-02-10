"""
Tests for ContainerRunningChecker with DockerCloudClient
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest
import os

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
    ),
    gpu_all=[1],
    load_analyzer=dm.LoadAnalyzerConfig(
        sleep_time=0.1,
        trigger_pipeline=dm.TriggerPipelineConfig(60),
        running_mean=dm.RunningMeanConfig(50, 100, 10),
    ),
    health_check=dm.HealthCheckerConfig(10),
    models=dm.ModelsRunnerConfig(
        ports=dm.PortConfig(
            sender_open_addr=5566,
            sender_sync_addr=5443,
            receiver_open_addr=4531,
            receiver_sync_addr=5654,
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
        status = await checker.check(model_instance)
        assert status.is_running
        assert status.reason is None
        assert status.model_instance == model_instance
    finally:
        cloud_client.stop_instance(model_instance)
