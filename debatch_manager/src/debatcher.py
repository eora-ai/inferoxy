"""
This module needed to recieve response objects from batch
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import List, Iterator, Optional, Iterable
from itertools import repeat

import plyvel  # type: ignore
from loguru import logger

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
        print(mini_batch)
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
    # Open conndection
    try:
        database = plyvel.DB(
            config.db_file,
        )
    except plyvel._plyvel.IOError as exc:
        raise IOError() from exc
    # Pull batch mapping from database
    batch_mapping_bytes = database.get(bytes(batch.uid, "utf-8"))
    batch_mapping = dm.BatchMapping.from_key_value(
        (bytes(batch.uid, "utf-8"), batch_mapping_bytes)
    )

    # Delete mapping
    database.delete(bytes(batch.uid, "utf-8"))
    database.close()

    return batch_mapping
