"""
Tests for src.alert_sender.alert_manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest

import src.data_models as dm
from src.alert_sender import AlertManager
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.health_checker.errors import ContainerExited, ContainerDoesNotExists

pytestmark = pytest.mark.asyncio

model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=512,
    run_on_gpu=False,
)
batch = dm.MinimalBatchObject(
    uid="0",
    requests_info=[],
    model=model,
    status=dm.Status.IN_QUEUE,
    source_id=None,
)
model_instance = dm.ModelInstance(
    model=model,
    name="Test1",
    sender=BaseSender(),
    receiver=BaseReceiver(),
    lock=True,
    hostname="",
    source_id="",
    running=True,
    current_processing_batch=batch,
)


async def test_send():
    input_queue, output_queue = InputBatchQueue(), OutputBatchQueue()
    alert_manager = AlertManager(input_queue, output_queue)
    error = ContainerExited("ContainerExited")
    await alert_manager.send(model_instance, error)
    response_batch = await output_queue.get()
    assert response_batch.error == str(error)


async def test_retry():
    input_queue, output_queue = InputBatchQueue(), OutputBatchQueue()
    alert_manager = AlertManager(input_queue, output_queue)
    error = ContainerDoesNotExists("ContainerDoesNotExists")
    await alert_manager.retry_task(model_instance, error)
    input_batch = input_queue.get_nowait(model)
    assert input_batch == batch
