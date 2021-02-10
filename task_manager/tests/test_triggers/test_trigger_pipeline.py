"""
Tests for src.load_analyzers.triggers.TriggerPipeline
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Dict
from functools import reduce
from collections import defaultdict

import src.data_models as dm
from src.batch_queue import OutputBatchQueue
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner

from src.load_analyzers.triggers import (
    TriggerPipeline,
    DecreaseTrigger,
    IncreaseTrigger,
)
from src.cloud_clients.mock_cloud_client import (
    MockCloudClient,
)


stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)

stub_stateful = dm.ModelObject(
    "stub-stateful",
    "registry.visionhub.ru/models/stub:v3",
    stateless=False,
    batch_size=128,
)

stub_config = dm.Config(
    zmq_output_address="",
    zmq_input_address="",
    gpu_all=[],
    load_analyzer=dm.LoadAnalyzerConfig(
        0.5,
        trigger_pipeline=dm.TriggerPipelineConfig(70),
        running_mean=dm.RunningMeanConfig(0.1, 1, 3),
    ),
    health_check=dm.HealthCheckerConfig(10),
    docker=dm.DockerConfig("", "", ""),
    models=dm.ModelsRunnerConfig(
        ports=dm.PortConfig(0, 0, 0, 0), zmq_config=dm.ZMQConfig(0, 0, 0, 0)
    ),
)


def test_decrease_stateful_in_pipeline():
    """
    Test that DecreaseTrigger with stateful model_instances does not removed after pipeline optimization
    """
    model_instance1 = dm.ModelInstance(
        model=stub_stateful,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    model_instance2 = dm.ModelInstance(
        model=stub_stateful,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    output_queue = OutputBatchQueue()
    model_instances_storage = ModelInstancesStorage(
        receiver_streams_combiner=ReceiverStreamsCombiner(
            output_batch_queue=output_queue
        )
    )
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)

    decrease_trigger1 = DecreaseTrigger(model_instance=model_instance1, stateless=False)
    decrease_trigger2 = DecreaseTrigger(model_instance=model_instance2, stateless=False)

    pipeline = TriggerPipeline(
        cloud_client=MockCloudClient(4, None),
        model_instances_storage=model_instances_storage,
        config=stub_config,
    )
    pipeline.append(decrease_trigger1)
    pipeline.append(decrease_trigger2)
    pipeline.optimize()
    assert pipeline.get_triggers() == [decrease_trigger1, decrease_trigger2]


def test_decrease_stateless_in_pipeline():
    """
    Left only one decrease trigger for stateless trigger
    """
    model_instance1 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    model_instance2 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    output_queue = OutputBatchQueue()
    model_instances_storage = ModelInstancesStorage(
        receiver_streams_combiner=ReceiverStreamsCombiner(
            output_batch_queue=output_queue
        )
    )
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)

    decrease_trigger1 = DecreaseTrigger(model=stub_model, stateless=True)
    decrease_trigger2 = DecreaseTrigger(model=stub_model, stateless=True)

    pipeline = TriggerPipeline(
        cloud_client=MockCloudClient(4, None),
        model_instances_storage=model_instances_storage,
        config=stub_config,
    )
    pipeline.append(decrease_trigger1)
    pipeline.append(decrease_trigger2)
    pipeline.optimize()
    assert pipeline.get_triggers() == [decrease_trigger1]


def test_not_enough_resources_decrease_in_pipeline():
    """
    Left all decerease triggers if there are no space to create new model instance
    """
    model_instance1 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    model_instance2 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    output_queue = OutputBatchQueue()
    model_instances_storage = ModelInstancesStorage(
        receiver_streams_combiner=ReceiverStreamsCombiner(
            output_batch_queue=output_queue
        )
    )
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)

    decrease_trigger1 = DecreaseTrigger(model=stub_model, stateless=True)
    decrease_trigger2 = DecreaseTrigger(model=stub_model, stateless=True)

    pipeline = TriggerPipeline(
        cloud_client=MockCloudClient(4, None),
        model_instances_storage=model_instances_storage,
        config=stub_config,
    )
    pipeline.append(decrease_trigger1)
    pipeline.append(decrease_trigger2)
    pipeline.optimize()
    assert pipeline.get_triggers() == [decrease_trigger1]


def test_percent_rule():
    """
    Check that after trieng append IncreaseTrigger, if number of model more than 70%
    """
    model_instance1 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    model_instance2 = dm.ModelInstance(
        model=stub_model,
        source_id=None,
        sender=BaseSender(),
        receiver=BaseReceiver(),
        lock=False,
        running=True,
        hostname="test",
    )
    output_queue = OutputBatchQueue()
    model_instances_storage = ModelInstancesStorage(
        receiver_streams_combiner=ReceiverStreamsCombiner(
            output_batch_queue=output_queue
        )
    )
    model_instances_storage.add_model_instance(model_instance1)
    model_instances_storage.add_model_instance(model_instance2)

    increase_trigger = IncreaseTrigger(model=stub_model)

    pipeline = TriggerPipeline(
        cloud_client=MockCloudClient(4, None),
        model_instances_storage=model_instances_storage,
        config=stub_config,
    )
    pipeline.append(increase_trigger)
    pipeline.optimize()
    assert pipeline.get_triggers() == []
