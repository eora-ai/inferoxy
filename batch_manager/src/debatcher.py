"""
This module needed to recieve response objects from batch
"""

import src.data_models as dm

from typing import List
from shared_modules.data_objects import ResponseObject, ResponseBatch


def debatch(
    batch: ResponseBatch, batch_mapping: dm.BatchMapping
) -> List[ResponseObject]:
    """
    Dissociate batch_object and update batch mapping

    Parameters
    ----------
    batch:
        Batch object

    batch_mapping:
        Mapping between request objects and batches
    """
    request_object_uids = batch_mapping.request_object_uids
    response_objects = []
    for i, request_object_uid in enumerate(request_object_uids):
        new_response_object = ResponseObject(
            uid=request_object_uid,
            model=batch.model,
            parameters=None,
            # TODO: check it
            source_id=batch_mapping.source_id[i],
            outputs=batch.outputs[i]
        )
        response_objects.append(new_response_object)

    return response_objects
