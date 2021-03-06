"""
Tests for ModelInstancesStorage
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest

import src.data_models as dm
from src.batch_queue import OutputBatchQueue
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner

pytestmark = pytest.mark.asyncio

stub_model = dm.ModelObject(
    "stub",
    "registry.visionhub.ru/models/stub:v3",
    stateless=True,
    batch_size=128,
)

stub_stateful = dm.ModelObject(
    "stub-stateful",
    "registry.visionhub.ru/models/stub:v3",
    stateless=False,
    batch_size=128,
    run_on_gpu=False,
)


async def test_add_model_instance():
    """
    Test for add_model_instance
    """
    model_instance = dm.ModelInstance(
        model=stub_model,
        name="",
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        hostname="",
        running=True,
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance)
    models_with_source_ids = (
        model_instances_storage.get_running_models_with_source_ids()
    )

    assert models_with_source_ids == [(None, stub_model)]


async def test_remove_model_instance():
    """
    Remove model instance fro model instances storage
    """

    model_instance = dm.ModelInstance(
        model=stub_model,
        name="",
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        hostname="",
        running=True,
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance)
    await model_instances_storage.remove_model_instance(model_instance=model_instance)
    models_with_source_ids = (
        model_instances_storage.get_running_models_with_source_ids()
    )

    assert models_with_source_ids == []


async def test_stateful_batch_routing():
    """
    Add three stateful model instances, but only one is compatible by source id
    """
    model_instance1 = dm.ModelInstance(
        model=stub_stateful,
        name="",
        source_id="test1",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="",
    )
    model_instance2 = dm.ModelInstance(
        model=stub_stateful,
        name="2",
        source_id="test2",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="",
    )
    model_instance3 = dm.ModelInstance(
        model=stub_stateful,
        name="3",
        source_id="test3",
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="",
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance1)
    model_instances_storage.add_model_instance(model_instance=model_instance2)
    model_instances_storage.add_model_instance(model_instance=model_instance3)

    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_stateful, source_id="test1"
        )
        == model_instance1
    )
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_stateful, source_id="test2"
        )
        == model_instance2
    )
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_stateful, source_id="test3"
        )
        == model_instance3
    )


async def test_stateless_batch_routing():
    """
    Add three stateless model instance, check that round robin
    """
    model_instance1 = dm.ModelInstance(
        model=stub_model,
        name="",
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        hostname="",
        running=True,
    )
    model_instance2 = dm.ModelInstance(
        model=stub_model,
        name="2",
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        hostname="",
        running=True,
    )
    model_instance3 = dm.ModelInstance(
        model=stub_model,
        name="3",
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="",
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance1)
    model_instances_storage.add_model_instance(model_instance=model_instance2)

    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_model, source_id=None
        )
        == model_instance1
    )
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_model, source_id=None
        )
        == model_instance2
    )
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_model, source_id=None
        )
        == model_instance1
    )

    model_instances_storage.add_model_instance(model_instance=model_instance3)
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_model, source_id=None
        )
        == model_instance2
    )
    assert (
        model_instances_storage.get_next_running_instance(
            model=stub_model, source_id=None
        )
        == model_instance3
    )
