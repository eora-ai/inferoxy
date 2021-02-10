"""
Tests for input and output queues
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio

import pytest
import numpy as np  # type: ignore
import src.data_models as dm

from src.exceptions import TagDoesNotExists
from src.batch_queue import InputBatchQueue, OutputBatchQueue

pytestmark = pytest.mark.asyncio

stub_model = dm.ModelObject(
    "stub",
    "registry.visionhub.ru/models/stub:v3",
    stateless=True,
    batch_size=128,
    run_on_gpu=False,
)

stub_stateful = dm.ModelObject(
    "stub-stateful",
    "registry.visionhub.ru/models/stub:v3",
    stateless=False,
    batch_size=128,
    run_on_gpu=False,
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
    request_info = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    await input_batch_queue.put(item)
    assert input_batch_queue.get_num_requests_in_queue(stub_model) == 1

    result = input_batch_queue.get_nowait(stub_model)
    assert input_batch_queue.get_num_requests_in_queue(stub_model) == 0
    assert result == item
    assert result.status == dm.Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_model)

    with pytest.raises(TagDoesNotExists):
        input_batch_queue.get_nowait(stub_model)


async def test_multiple_elements_input_queue():
    """
    Put three elements in the queue and try to get them
    """
    input_batch_queue = InputBatchQueue()
    request_info1 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item1 = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info1],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    request_info2 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item2 = dm.MinimalBatchObject(
        uid="2",
        requests_info=[request_info2],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    request_info3 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item3 = dm.MinimalBatchObject(
        uid="3",
        requests_info=[request_info3],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    await input_batch_queue.put(item1)
    await input_batch_queue.put(item2)
    await input_batch_queue.put(item3)
    result = input_batch_queue.get_nowait(stub_model)
    assert result == item1
    assert result.status == dm.Status.IN_QUEUE

    result = input_batch_queue.get_nowait(stub_model)
    assert result == item2
    assert result.status == dm.Status.IN_QUEUE

    result = input_batch_queue.get_nowait(stub_model)
    assert result == item3
    assert result.status == dm.Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_model)


async def test_stateful_models():
    """
    Test stateful model
    """
    request_info = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="test",
    )
    input_batch_queue = InputBatchQueue()
    await input_batch_queue.put(item)

    result = input_batch_queue.get_nowait(stub_stateful, source_id="test")

    assert result == item
    assert result.status == dm.Status.IN_QUEUE

    with pytest.raises(asyncio.QueueEmpty):
        input_batch_queue.get_nowait(stub_stateful, source_id="test")
