"""
Tests for RunningMeanStatelessChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import pytest
import numpy as np  # type: ignore

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.utils.data_transfers import Sender, Receiver
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.load_analyzers.checkers import RunningMeanStatelessChecker
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

stub_config = dm.Config(
    "",
    "",
    "",
    "",
    "",
    [],
    dm.LoadAnalyzerConfig(
        0.5,
        trigger_pipeline=dm.TriggerPipelineConfig(70),
        running_mean=dm.RunningMeanConfig(0.1, 1, 3),
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
    stub_config.load_analyzer.running_mean = dm.RunningMeanConfig(0.1, 1, 3)
    checker = RunningMeanStatelessChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, stub_config
    )
    triggers = checker.make_triggers()
    assert triggers == []


async def test_low_load():
    """
    Test with low load
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    stub_config.load_analyzer.running_mean = dm.RunningMeanConfig(5, 10, 10)
    checker = RunningMeanStatelessChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, stub_config
    )
    model_instances_storage.add_model_instance(
        dm.ModelInstance(
            model=stub_model,
            source_id=None,
            sender=Sender(),
            receiver=Receiver(),
            lock=False,
            running=True,
            container_name="test",
        )
    )

    model_instances_storage.add_model_instance(
        dm.ModelInstance(
            model=stub_model,
            source_id=None,
            sender=Sender(),
            receiver=Receiver(),
            lock=False,
            running=True,
            container_name="test",
        )
    )

    response1 = dm.ResponseBatch(
        uid="1",
        inputs=[np.array(range(10))],
        outputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.PROCESSED,
        processed_at=10,
        started_at=9,
    )

    response2 = dm.ResponseBatch(
        uid="2",
        inputs=[np.array(range(10))],
        outputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.PROCESSED,
        processed_at=11,
        started_at=10,
    )

    await output_batch_queue.put(response1)
    await output_batch_queue.put(response2)

    # In output queue we store that model `stub_model` take 1 second to process one `request_object`

    request1 = dm.RequestBatch(
        uid="3",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    request2 = dm.RequestBatch(
        uid="4",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    await input_batch_queue.put(request1)
    await input_batch_queue.put(request2)

    # In output queue we store two `request_object`s that will take 2 seconds in total

    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], DecreaseTrigger)


async def test_high_load():
    """
    Test with high load
    """
    input_batch_queue = InputBatchQueue()
    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    model_instances_storage = ModelInstancesStorage(receiver_streams_combiner)
    model_instances_storage.add_model_instance(
        dm.ModelInstance(
            model=stub_model,
            source_id=None,
            sender=Sender(),
            receiver=Receiver(),
            lock=False,
            running=True,
            container_name="test",
        )
    )

    model_instances_storage.add_model_instance(
        dm.ModelInstance(
            model=stub_model,
            source_id=None,
            sender=Sender(),
            receiver=Receiver(),
            lock=False,
            running=True,
            container_name="test",
        )
    )
    stub_config.load_analyzer.running_mean = dm.RunningMeanConfig(0.1, 3, 3)
    checker = RunningMeanStatelessChecker(
        model_instances_storage, input_batch_queue, output_batch_queue, stub_config
    )

    response1 = dm.ResponseBatch(
        uid="1",
        inputs=[np.array(range(10))],
        outputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.PROCESSED,
        processed_at=10,
        started_at=9,
    )

    response2 = dm.ResponseBatch(
        uid="2",
        inputs=[np.array(range(10))],
        outputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.PROCESSED,
        processed_at=11,
        started_at=10,
    )

    await output_batch_queue.put(response1)
    await output_batch_queue.put(response2)

    # Average processing time for `stub_model` is 1 second

    request1 = dm.RequestBatch(
        uid="3",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    request2 = dm.RequestBatch(
        uid="4",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    request3 = dm.RequestBatch(
        uid="5",
        inputs=[
            np.array(range(10)),
            np.array(range(10)),
            np.array(range(10)),
            np.array(range(10)),
            np.array(range(10)),
        ],
        parameters=[{}, {}, {}, {}, {}],
        model=stub_model,
        status=dm.Status.CREATED,
    )
    await input_batch_queue.put(request1)
    await input_batch_queue.put(request2)
    await input_batch_queue.put(request3)

    # In queue 7 requests * 1 second / 2 models> max_threshold=2
    # So checker will create an IncreaseTrigger

    triggers = checker.make_triggers()
    assert len(triggers) == 1
    assert isinstance(triggers[0], IncreaseTrigger)