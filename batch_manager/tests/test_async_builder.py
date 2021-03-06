"""
Test for async wrapper of builder
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
import asyncio
from typing import AsyncIterable

import pytest
import numpy as np  # type: ignore

import src.data_models as dm
from src.builder import builder
from shared_modules.utils import uuid4_string_generator


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
        t = False
        while True:
            if t:
                await asyncio.sleep(1)
                continue
            request_info = dm.RequestInfo(
                input=np.array(range(10)),
                parameters={},
            )
            yield dm.RequestObject(
                uid=next(uuid4_string_generator()),
                request_info=request_info,
                source_id="internal_sportrecs_1",
                model=stateless_model,
            )
            t = True

    before = time.time()
    async for (_, _) in builder(async_request_generator()):
        assert time.time() - before > 0.01
        break
    else:
        assert False


async def test_by_full_interrupt():
    """
    Test that if batch is full it will be sent immediately
    """

    async def async_request_generator() -> AsyncIterable[dm.RequestObject]:
        await asyncio.sleep(0.1)
        request_info1 = dm.RequestInfo(
            input=np.array(range(10)),
            parameters={},
        )
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            request_info=request_info1,
            source_id="internal_sportrecs_1",
            model=stateless_model,
        )
        request_info2 = dm.RequestInfo(
            input=np.array(range(10)),
            parameters={},
        )
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            request_info=request_info2,
            source_id="internal_sportrecs_1",
            model=stateless_model,
        )
        request_info3 = dm.RequestInfo(
            input=np.array(range(10)),
            parameters={},
        )
        yield dm.RequestObject(
            uid=next(uuid4_string_generator()),
            request_info=request_info3,
            source_id="internal_sportrecs_1",
            model=stateless_model,
        )

    async for (_, _) in builder(async_request_generator()):
        assert True
        break
    else:
        assert False
