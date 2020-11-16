"""
This module needed to build batch from request objects.
Main bussines logic of BatchManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Tuple, Generator, AsyncIterable
from functools import reduce
import asyncio

from aiostream import stream

import src.data_models as dm
from src.utils import uuid4_string_generator


async def builder(
    request_stream: AsyncIterable[dm.RequestObject],
) -> AsyncIterable[Tuple[dm.BatchObject, dm.BatchMapping]]:
    """
    From async generator of request build two genrators:
    first one is an async generator of BatchObject,
    and second one is an async generator of BatchMapping

    Parameters
    ----------
    request_stream
        Infinite stream of request objects
    """
    batches = dm.Batches(batches=[])

    async def result_time_interrupt(batches):
        while True:
            await asyncio.sleep(0.1)
            _batches, batches.batches = batches[:], []
            mappings = map(build_mapping_batch, _batches)
            batches_and_mappings = list(zip(map(lambda x: x.batch, _batches), mappings))
            for batch, mapping in batches_and_mappings:
                yield (batch, mapping)

    async def result_complete_batches(batches):
        async for request_object in request_stream:
            batches.batches = build_batches(
                [request_object], existing_batches=batches
            ).batches
            (
                completed_batch,
                batches,
            ) = split_on_complete_and_uncomplete_batches(batches)
            for batch_with_requests in completed_batch.batches:
                mapping = build_mapping_batch(batch_with_requests)
                yield (batch_with_requests.batch, mapping)

    combine = stream.merge(
        result_time_interrupt(batches),
        result_complete_batches(batches),
    )
    async with combine.stream() as streamer:
        async for (batch, mapping) in streamer:
            yield (batch, mapping)


def split_on_complete_and_uncomplete_batches(
    batches: dm.Batches,
) -> Tuple[dm.Batches, dm.Batches]:
    """
    Separate batches on full batches and not full

    Parameters
    ----------
    batches
        List of batches

    Returns
    -------
        Tuple of filtered list of batches, first elem is completed batches
            and second is uncompleted batches
    """

    def filter_func(batch_with_requests):
        return (
            batch_with_requests.batch.model.batch_size == batch_with_requests.batch.size
        )

    completed_batches = dm.Batches(list(filter(filter_func, batches.batches)))

    batches.batches = list(filter(lambda x: not filter_func(x), batches.batches))

    return (
        completed_batches,
        batches,
    )


def build_batches(
    request_objects: List[dm.RequestObject],
    existing_batches: dm.Batches = None,
    uid_generator: Generator[str, None, None] = None,
) -> dm.Batches:
    """
    Aggregate request_objects by model. If model is statefull aggregate by source_id also.

    Parameters
    ----------
    request_objets:
        Not ordered request objects
    existing_batches:
        Already aggregated batches
    uid_generator:
        Uniq identifier generator

    Returns
    -------
    dm.Batches
        List of dm.BatchWithRelatedRequestObjects,
        that contains information of batch and related request objects
    """

    if uid_generator is None:
        uid_generator = uuid4_string_generator()

    def aggregate_function(batch_request_objects, request_object):
        for batch_with_request_objects in batch_request_objects:
            if (
                batch_with_request_objects.batch.model == request_object.model
                and batch_with_request_objects.batch.size
                < batch_with_request_objects.batch.model.batch_size
            ):
                if (
                    not batch_with_request_objects.batch.model.stateless
                    and batch_with_request_objects.request_objects[-1].source_id
                    != request_object.source_id
                ):
                    continue
                batch_with_request_objects.batch.inputs.append(request_object.inputs)
                batch_with_request_objects.batch.parameters.append(
                    request_object.parameters
                )
                batch_with_request_objects.request_objects.append(request_object)
                break
        else:
            new_batch = dm.BatchObject(
                uid=next(uid_generator),
                inputs=[request_object.inputs],
                parameters=[request_object.parameters],
                model=request_object.model,
            )
            batch_request_objects.append(
                dm.BatchWithRelatedRequestObjects(
                    batch=new_batch, request_objects=[request_object]
                )
            )
        return batch_request_objects

    return dm.Batches(
        batches=list(
            reduce(
                aggregate_function,
                request_objects,
                existing_batches.batches if existing_batches else [],
            )
        )
    )


def build_mapping_batch(
    batch_with_requests: dm.BatchWithRelatedRequestObjects,
) -> dm.BatchMapping:
    """
    Connect list of request_objects with batch

    Parameters
    ----------
    batch_with_requests
        pass

    Returns
    -------
    dm.BatchMapping
        Mapping between batch and request objects

    Raises
    ------
    ValueError
        If batch and request_objects are empty or None
    """
    batch = batch_with_requests.batch
    request_objects = batch_with_requests.request_objects
    if not isinstance(batch, dm.BatchObject):
        raise ValueError(f"batch must be of type {dm.BatchObject}")
    if not isinstance(request_objects, list) and len(request_objects) == 0:
        raise ValueError("request_object must be of non empty list")

    return dm.BatchMapping(
        batch_uid=batch.uid,
        request_object_uids=list(map(lambda lo: lo.uid, request_objects)),
        source_ids=list(map(lambda lo: lo.source_id, request_objects)),
    )
