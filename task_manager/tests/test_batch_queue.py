"""
Tests for input and output queues
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio

import pytest
import numpy as np  # type: ignore

from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.exceptions import TagDoesNotExists
from shared_modules.data_objects import (
    MinimalBatchObject,
    ModelObject,
    Status,
)

pytestmark = pytest.mark.asyncio

stub_model = ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)

stub_stateful = ModelObject(
    "stub-stateful",
    "registry.visionhub.ru/models/stub:v3",
    stateless=False,
    batch_size=128,
)


async def test_empty_queue():
    """
    Check TagDoesNotExists exception
    """

    input_batch_queue = InputBatchQueue()
    with pytest.raises(TagDoesNotExists):
        input_batch_queue.get_nowait(stub_model)


async def test_one_element_input_queue():
    """
    Put one element in input queue, and try to get it
    """

    input_batch_queue = InputBatchQueue()
    item = MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=Status.CREATED,
    )
    await input_batch_queue.put(item, stub_model)
    result = input_batch_queue.get_nowait(stub_model)
    assert result == item
    assert result.status == Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_model)

    with pytest.raises(TagDoesNotExists):
        input_batch_queue.get_nowait(stub_model)


async def test_multiple_elements_input_queue():
    """
    Put three elements in the queue and try to get them
    """
    input_batch_queue = InputBatchQueue()
    item1 = MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=Status.CREATED,
    )
    item2 = MinimalBatchObject(
        uid="2",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=Status.CREATED,
    )
    item3 = MinimalBatchObject(
        uid="3",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=Status.CREATED,
    )
    await input_batch_queue.put(item1, stub_model)
    await input_batch_queue.put(item2, stub_model)
    await input_batch_queue.put(item3, stub_model)
    result = input_batch_queue.get_nowait(stub_model)
    assert result == item1
    assert result.status == Status.IN_QUEUE

    result = input_batch_queue.get_nowait(stub_model)
    assert result == item2
    assert result.status == Status.IN_QUEUE

    result = input_batch_queue.get_nowait(stub_model)
    assert result == item3
    assert result.status == Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_model)


async def test_stateful_models():
    """
    Test stateful model
    """
    item = MinimalBatchObject(
        uid="1",
        inputs=np.array(range(10)),
        parameters=[{}],
        model=stub_stateful,
        status=Status.CREATED,
        source_id="test",
    )
    input_batch_queue = InputBatchQueue()
    await input_batch_queue.put(item, stub_stateful)

    result = input_batch_queue.get_nowait(stub_stateful, source_id="test")

    assert result == item
    assert result.status == Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_stateful, source_id="test")
