"""
This module needed to build batch from request objects.
Main bussines logic of BatchManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Tuple, Generator
from functools import reduce

import src.data_models as dm


def build_batch(
    request_objects: List[dm.RequestObject],
    existing_batches: List[Tuple[dm.BatchObject, List[dm.RequestObject]]] = None,
    uid_generator: Generator[str, None, None] = None,
) -> List[Tuple[dm.BatchObject, List[dm.RequestObject]]]:
    """
    Aggregate request_objects by model. If model is statefull aggregate by source_id also.

    Parameters
    ----------
    request_objets
        Not ordered request objects

    Returns
    -------
    List[(dm.BatchObject, List[dm.RequestObject])]
        List of tuples where first element is batch object
        and second element is a list of request objects.
    """

    def aggregate_function(batch_request_objects, request_object):
        for (batch, request_objects) in batch_request_objects:
            if batch.model == request_object.model and (
                not batch.model.stateless
                or request_objects[-1].source_id == request_object.source_id
            ):
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
    request_objets: List[dm.RequestObject],
    uid_generator: Generator[str, None, None] = None,
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
    """
    return []
