"""
Test for async wrapper of builder
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
import asyncio
from typing import AsyncIterable

import numpy as np  # type: ignore
import pytest


import src.data_models as dm
from src.builder import builder
from src.utils import uuid4_string_generator


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

stateless_model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v3",
    stateless=True,
    batch_size=3,
)


async def test_by_time_interrupt():
    """
    Test that if batch is not full it will be sent after 0.1s
    """

    async def async_request_generator() -> AsyncIterable[dm.RequestObject]:
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            inputs=np.array(range(10)),
            source_id="internal_sportrecs_1",
            parameters={},
            model=stateless_model,
        )

    before = time.time()
    async for (_, _) in builder(async_request_generator()):
        assert time.time() - before > 0.1
        break
    else:
        assert False


async def test_by_full_interrupt():
    """
    Test that if batch is full it will be sent immediately
    """

    async def async_request_generator() -> AsyncIterable[dm.RequestObject]:
        await asyncio.sleep(0.1)
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            inputs=np.array(range(10)),
            source_id="internal_sportrecs_1",
            parameters={},
            model=stateless_model,
        )
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            inputs=np.array(range(10)),
            source_id="internal_sportrecs_1",
            parameters={},
            model=stateless_model,
        )
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            inputs=np.array(range(10)),
            source_id="internal_sportrecs_1",
            parameters={},
            model=stateless_model,
        )

    async for (_, _) in builder(async_request_generator()):
        assert True
        break
    else:
        assert False
