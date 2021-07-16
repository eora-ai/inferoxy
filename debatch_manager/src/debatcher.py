"""
This module needed to recieve response objects from batch
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import List, Iterator, Optional, Iterable
from itertools import repeat


from shared_modules.utils import uuid4_string_generator
import src.data_models as dm


def debatch(
    batch: dm.ResponseBatch,
    batch_mapping: dm.BatchMapping,
) -> List[dm.ResponseObject]:
    """
    Dissociate batch_object and update batch mapping

    Parameters
    ----------
    batch:
        Batch object

    batch_mapping:
        Mapping between request objects and batches
    """

    response_objects = []
    error = batch.error
    mini_batches: Iterator[Iterable[Optional[dm.ResponseInfo]]] = (
        repeat([None])
        if error or batch.mini_batches is None
        else iter(batch.mini_batches)
    )
    for (request_object_uid, source_id) in iter(batch_mapping):
        mini_batch = next(mini_batches)
        for response_info in mini_batch:
            new_response_object = dm.ResponseObject(
                uid=request_object_uid,
                model=batch.model,
                source_id=source_id,
                response_info=response_info,
                error=error,
            )
            response_objects.append(new_response_object)

    return response_objects
