"""
This module needed to build batch from request objects.
Main bussines logic of BatchManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Tuple, Generator
from functools import reduce, partial

import src.data_models as dm
from src.utils import uuid4_string_generator


def build_batch(
    request_objects: List[dm.RequestObject],
    existing_batches: List[Tuple[dm.BatchObject, List[dm.RequestObject]]] = None,
    uid_generator: Generator[str, None, None] = None,
) -> List[Tuple[dm.BatchObject, List[dm.RequestObject]]]:
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
    List[(dm.BatchObject, List[dm.RequestObject])]
        List of tuples where first element is batch object
        and second element is a list of request objects.
    """

    if uid_generator is None:
        uid_generator = uuid4_string_generator()

    def aggregate_function(batch_request_objects, request_object):
        for (batch, request_objects) in batch_request_objects:
            if (
                batch.model == request_object.model
                and batch.size < batch.model.batch_size
            ):
                if (
                    not batch.model.stateless
                    and request_objects[-1].source_id != request_object.source_id
                ):
                    continue
                batch.inputs.append(request_object.inputs)
                batch.parameters.append(request_object.parameters)
                request_objects.append(request_object)
                break
        else:
            new_batch = dm.BatchObject(
                uid=next(uid_generator),
                inputs=[request_object.inputs],
                parameters=[request_object.parameters],
                model=request_object.model,
            )
            batch_request_objects.append((new_batch, [request_object]))
        return batch_request_objects

    return list(
        reduce(
            aggregate_function,
            request_objects,
            existing_batches if existing_batches else [],
        )
    )


def build_mapping_batch(
    batch: dm.BatchObject,
    request_objects: List[dm.RequestObject],
) -> dm.BatchMapping:
    """
    Connect list of request_objects with batch

    Parameters
    ----------
    batch:
        Batch object, that contain request objects
    request_objects:
        Request Objects

    Returns
    -------
    dm.BatchMapping
        Mapping between batch and request objects

    Raises
    ------
    ValueError
        If batch and request_objects are empty or None
    """
    if not isinstance(batch, dm.BatchObject):
        raise ValueError(f"batch must be of type {dm.BatchObject}")
    if not isinstance(request_objects, list) and len(request_objects) == 0:
        raise ValueError("request_object must be of non empty list")

    return dm.BatchMapping(
        batch_uid=batch.uid,
        request_object_uids=list(map(lambda lo: lo.uid, request_objects)),
        source_ids=list(map(lambda lo: lo.source_id, request_objects)),
    )
