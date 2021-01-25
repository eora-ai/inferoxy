"""
Tests for StatefulChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest
import numpy as np  # type: ignore

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.load_analyzers.checkers import StatefulChecker
from src.load_analyzers.triggers import IncreaseTrigger, DecreaseTrigger
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver

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
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_requested_one_stateless_model():
    """
    Test for one requested model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    item = dm.MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    await input_batch_queue.put(item)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_requested_one_stateful_model():
    """
    Test for requested stateful model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    item = dm.MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="1",
    )
    await input_batch_queue.put(item)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_stateful


async def test_requested_many_stateful_model():
    """
    Test for requested many stateful model
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    item1 = dm.MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="1",
    )
    item2 = dm.MinimalBatchObject(
        uid="2",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="2",
    )
    await input_batch_queue.put(item1)
    await input_batch_queue.put(item2)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 2
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_stateful


async def test_decrease_stateful_instance():
    """
    Test that model not requested
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    item1 = dm.MinimalBatchObject(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="1",
    )
    await input_batch_queue.put(item1)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    model_instance1 = dm.ModelInstance(
        stub_stateful,
        "1",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=True,
        running=True,
        container_name="test",
    )
    model_instance2 = dm.ModelInstance(
        stub_stateful,
        None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        container_name="test",
    )
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], DecreaseTrigger)
    assert triggers[0].model_instance == model_instance2
