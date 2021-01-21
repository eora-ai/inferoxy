"""
This module needed to recieve response objects from batch
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import src.data_models as dm
import plyvel  # type: ignore

from typing import List


def debatch(
    batch: dm.ResponseBatch, batch_mapping: dm.BatchMapping
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
    request_object_uids = batch_mapping.request_object_uids
    response_objects = []
    for i, request_object_uid in enumerate(request_object_uids):

        # Create response object
        new_response_object = dm.ResponseObject(
            uid=request_object_uid,
            model=batch.model,
            source_id=batch_mapping.source_ids[i],
            output=[batch.outputs[i]],
        )
        response_objects.append(new_response_object)

    return response_objects


def pull_batch_mapping(config: dm.Config, batch: dm.ResponseBatch) -> dm.BatchMapping:
    """
    Retrieve dm.BatchMapping from database

    Parameters
    ---------
    config:
        Config of database
    batch:
        Response Batch object
    """
    try:
        # Open conndection
        database = plyvel.DB(
            config.db_file,
        )

        # Pull batch mapping from database
        batch_mapping_bytes = database.get(bytes(batch.uid, "utf-8"))
        batch_mapping = dm.BatchMapping.from_key_value(
            (bytes(batch.uid, "utf-8"), batch_mapping_bytes)
        )

        # Delete mapping
        database.delete(bytes(batch.uid, "utf-8"))

        # Close connection
        database.close()
        return batch_mapping
    except IOError:
        raise RuntimeError("Failed to open database")
