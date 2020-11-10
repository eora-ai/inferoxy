"""
This module needed to build batch from request objects.
Main bussines logic of BatchManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List

import src.data_models as dm


def build_batch(
    request_objets: List[dm.RequestObject],
) -> List[(dm.BatchObject, List[dm.RequestObject])]:
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
    return []


def build_mapping_batch(
    batch: dm.BatchObject,
    request_objets: List[dm.RequestObject],
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
