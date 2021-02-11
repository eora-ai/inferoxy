"""
Tests for EnoughResourcesChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest
import numpy as np  # type: ignore

import src.data_models as dm
from src.load_analyzers.triggers import IncreaseTrigger
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.load_analyzers.checkers import EnoughResourcesChecker
from src.receiver_streams_combiner import ReceiverStreamsCombiner

pytestmark = pytest.mark.asyncio

stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)
stub_stateful = dm.ModelObject(
    "stub-stateful",
    "registry.visionhub.ru/models/stub:v3",
    stateless=False,
    batch_size=128,
)


async def test_requested_zero_models():
    """
    Test for zero requested model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = EnoughResourcesChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, None
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_requested_one_model():
    """
    Test for one requested model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
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
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = EnoughResourcesChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_model


async def test_requested_many_model():
    """
    Test for many requested model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
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
    await input_batch_queue.put(item)
    await input_batch_queue.put(item)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = EnoughResourcesChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_model


async def test_requested_stateful_model():
    """
    Test for requested stateful model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    request_info = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="1",
    )
    await input_batch_queue.put(item)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = EnoughResourcesChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert triggers == []
