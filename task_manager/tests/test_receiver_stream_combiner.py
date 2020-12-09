"""
Tests for receiver streams combiner
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import AsyncIterator

import numpy as np
import pytest

from src.batch_queue import OutputBatchQueue
from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.utils.data_transfers import Receiver
import src.data_models as dm

pytestmark = pytest.mark.asyncio


stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)


async def test_empty_queue():
    """
    Check that queue is empty if sources is empty
    """

    async def stop():
        await asyncio.sleep(1)

    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    await asyncio.wait(
        [receiver_streams_combiner.converter(), stop()], return_when="FIRST_COMPLETED"
    )
    with pytest.raises(asyncio.QueueEmpty):
        output_batch_queue.get_nowait()


async def test_one_element_in_output_queue():
    """
    Receiver combiner accept one response batch and put it into output batch queue
    """

    batch_dict = dict(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.IN_QUEUE,
    )

    class StubReceiver(Receiver):
        async def receive(self) -> AsyncIterator[dict]:
            yield batch_dict

    receiver = StubReceiver()

    async def stop():
        await asyncio.sleep(1)

    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    receiver_streams_combiner.add_listener(receiver)
    await asyncio.wait(
        [receiver_streams_combiner.converter(), stop()], return_when="FIRST_COMPLETED"
    )
    response_batch = output_batch_queue.get_nowait()
    assert response_batch == dm.ResponseBatch(**batch_dict)

    with pytest.raises(asyncio.QueueEmpty):
        output_batch_queue.get_nowait()


async def test_multiple_element_in_output_queue():
    """
    Receiver combiner accept one response batch and put it into output batch queue
    """

    batch_dict = dict(
        uid="1",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=stub_model,
        status=dm.Status.IN_QUEUE,
    )

    class StubReceiver(Receiver):
        async def receive(self) -> AsyncIterator[dict]:
            yield batch_dict
            yield batch_dict
            yield batch_dict

    receiver = StubReceiver()

    async def stop():
        await asyncio.sleep(1)

    output_batch_queue = OutputBatchQueue()
    receiver_streams_combiner = ReceiverStreamsCombiner(output_batch_queue)
    receiver_streams_combiner.add_listener(receiver)
    await asyncio.wait(
        [receiver_streams_combiner.converter(), stop()], return_when="FIRST_COMPLETED"
    )
    response_batch = output_batch_queue.get_nowait()
    assert response_batch == dm.ResponseBatch(**batch_dict)
    response_batch = output_batch_queue.get_nowait()
    assert response_batch == dm.ResponseBatch(**batch_dict)
    response_batch = output_batch_queue.get_nowait()
    assert response_batch == dm.ResponseBatch(**batch_dict)

    with pytest.raises(asyncio.QueueEmpty):
        output_batch_queue.get_nowait()
