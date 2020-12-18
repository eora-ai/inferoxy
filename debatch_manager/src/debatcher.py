"""
This module needed to recieve response objects from batch
"""

import src.data_models as dm
import plyvel  # type: ignore

from typing import List
from shared_modules.data_objects import (
    ResponseObject,
    ResponseBatch,
    BatchMapping
)


def debatch(
    batch: ResponseBatch, batch_mapping: BatchMapping
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

        # Merge outputs and pictures from response batch
        outputs = batch.outputs[i]
        pictures = batch.pictures[i]
        response_output = [{'outputs': outputs, 'pictures': pictures}]

        # Create response object
        new_response_object = ResponseObject(
            uid=request_object_uid,
            model=batch.model,
            # TODO: Change params
            parameters=None,
            source_id=batch_mapping.source_ids[i],
            # TODO: Change the outputs
            # Should be List[Dict[str, np.ndarray]]
            output=response_output
        )
        response_objects.append(new_response_object)

    return response_objects


def pull_batch_mapping(
    config: dm.Config,
    batch: ResponseBatch
) -> BatchMapping:
    """
    Retrieve BatchMapping from database

    Parameters
    ---------
    config:
        Config of database
    batch:
        Response Batch object
    """
    database = plyvel.DB(
        config.db_file,
    )
    # TODO: check ability to pop by property
    batch_mapping = database.pop(batch_uid=batch.uid)
    return batch_mapping
