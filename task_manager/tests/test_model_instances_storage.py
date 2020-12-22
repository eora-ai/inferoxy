"""
Tests for ModelInstancesStorage
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.batch_queue import OutputBatchQueue
import src.data_models as dm
from src.utils.data_transfers import Sender, Receiver

stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)


def test_add_model_instance():
    """
    Test for add_model_instance
    """
    model_instance = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=Sender(),
        receiver=Receiver(),
        lock=False,
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance)
    models_with_source_ids = (
        model_instances_storage.get_running_models_with_source_ids()
    )

    assert models_with_source_ids == [(None, stub_model)]


def test_remove_model_instance():
    """
    Remove model instance fro model instances storage
    """

    model_instance = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=Sender(),
        receiver=Receiver(),
        lock=False,
    )
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)

    model_instances_storage.add_model_instance(model_instance=model_instance)
    model_instances_storage.remove_model_instance(model_instance=model_instance)
    models_with_source_ids = (
        model_instances_storage.get_running_models_with_source_ids()
    )

    assert models_with_source_ids == []
