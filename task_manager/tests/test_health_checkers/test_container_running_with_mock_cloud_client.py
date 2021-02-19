"""
Tests for ContainerRunningChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest

import src.data_models as dm
from src.cloud_clients.mock_cloud_client import MockCloudClient
from src.health_checker.container_running_checker import ContainerRunningChecker, Status

pytestmark = pytest.mark.asyncio


model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=512,
    run_on_gpu=False,
)


async def test_positive():
    """
    This test is checking that mockcloudclient returns True
    """
    mock_cloud_client = MockCloudClient(2, None)
    model_instance = mock_cloud_client.start_instance(model)
    checker = ContainerRunningChecker(mock_cloud_client)
    status = checker.check(model_instance)
    assert status.is_running
    assert status.reason is None
    assert status.model_instance == model_instance


async def test_negative():
    """
    This test is checking that mockcloudclient returns False
    """
    mock_cloud_client = MockCloudClient(2, None)
    model_instance = mock_cloud_client.start_instance(model)
    model_instance.running = False
    checker = ContainerRunningChecker(mock_cloud_client)
    status = checker.check(model_instance)
    assert not status.is_running
    assert not status.reason is None
    assert status.model_instance == model_instance
