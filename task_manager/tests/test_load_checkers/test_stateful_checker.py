"""
Tests for StatefulChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import time

import pytest
import numpy as np  # type: ignore

import src.data_models as dm
from src.utils.data_transfers.sender import BaseSender
from src.load_analyzers.checkers import StatefulChecker
from src.utils.data_transfers.receiver import BaseReceiver
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.load_analyzers.triggers import IncreaseTrigger, DecreaseTrigger

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
config = dm.Config(
    zmq_input_address="",
    zmq_output_address="",
    cloud_client=dm.DockerConfig(
        registry="registry.visionhub.ru",
        login=os.environ.get("DOCKER_LOGIN", ""),
        password=os.environ.get("DOCKER_PASSWORD", ""),
        network=os.environ.get("DOCKER_NETWORK", ""),
    ),
    gpu_all=[1],
    load_analyzer=dm.LoadAnalyzerConfig(
        sleep_time=0.1,
        trigger_pipeline=dm.TriggerPipelineConfig(max_model_percent=60),
        running_mean=dm.RunningMeanConfig(
            min_threshold=50, max_threshold=100, window_size=10
        ),
        stateful_checker=dm.StatefulChecker(keep_model=10),
    ),
    health_check=dm.HealthCheckerConfig(connection_idle_timeout=10),
    models=dm.ModelsRunnerConfig(
        ports=dm.PortConfig(
            sender_open_addr=5566,
            receiver_open_addr=4531,
        ),
        zmq_config=dm.ZMQConfig(sndhwm=123, rcvhwm=121, sndtimeo=123, rcvtimeo=123),
    ),
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
        model_instances_storage, input_batch_queue, output_batch_queue, config=config
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_requested_one_stateless_model():
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
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, config=config
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_requested_one_stateful_model():
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
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, config=config
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

    request_info1 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item1 = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info1],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="1",
    )
    request_info2 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item2 = dm.MinimalBatchObject(
        uid="2",
        requests_info=[request_info2],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="2",
    )
    await input_batch_queue.put(item1)
    await input_batch_queue.put(item2)
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, config=config
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 2
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_stateful


async def test_free_model_instance_after_some_time():
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()

    request_info1 = dm.RequestInfo(
        input=np.array(range(10)),
        parameters={},
    )
    item1 = dm.MinimalBatchObject(
        uid="1",
        requests_info=[request_info1],
        model=stub_stateful,
        status=dm.Status.CREATED,
        source_id="new_source_id",
    )
    await input_batch_queue.put(item1)

    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    bs = BaseSender()
    bs.last_sent_batch = (
        time.time() - config.load_analyzer.stateful_checker.keep_model - 1
    )
    model_instance = dm.ModelInstance(
        stub_stateful,
        "previous_source_id",
        bs,
        BaseReceiver(),
        lock=False,
        hostname="test",
        running=True,
        name="test",
        num_gpu=None,
        current_processing_batch=None,
    )
    model_instances_storage.add_model_instance(model_instance)
    checker = StatefulChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, config=config
    )
    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], IncreaseTrigger)
    assert triggers[0].model == stub_stateful

    new_triggers = checker.make_triggers()
    assert len(new_triggers) == 0
    assert model_instance.source_id == "new_source_id"