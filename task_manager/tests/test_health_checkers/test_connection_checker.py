"""
Tests for connection checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time

import pytest

import src.data_models as dm
from src.utils.data_transfers.receiver import BaseReceiver
from src.utils.data_transfers.sender import BaseSender
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


async def test_was_received_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None))
    result = await checker.check(model_instance)
    assert result == Status(model_instance, True)


async def test_wasnot_received_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None))
    model_instance.receiver.last_received_batch = time.time() - 100
    result = await checker.check(model_instance)
    assert result == Status(model_instance, True)


async def test_wasnot_received_sent_in_10_seconds():
    model_instance = dm.ModelInstance(
        model=model,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        hostname="",
        source_id="",
        running=True,
    )
    checker = ConnectionChecker(MockCloudClient(2, None))
    model_instance.receiver.last_received_batch = time.time() - 100
    model_instance.sender.last_sent_batch = time.time() - 100
    result = await checker.check(model_instance)
    assert result == Status(
        model_instance, False, "Nothing was sent or received in 10 seconds"
    )


async def test_model_doesnot_locked():
    model_instance = dm.ModelInstance(
        model=model,
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
    result = await checker.check(model_instance)
    assert result == Status(model_instance, True)
