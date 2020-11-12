"""
Data object definitions
"""
__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import json
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class Config:
    """
    Configuration of batch_manager

    Parameters
    ----------
    zmq_input_address:
        Address of zreomq socket ipc for input requests
    zmq_output_address:
        Address of zreomq socket ipc for result batches
    """

    zmq_input_address: str
    zmq_output_address: str


@dataclass
class ModelObject:
    """
    Represents model. Need for Task manager to know which model and how to start it.

    Parameters
    ----------
    name:
        Name of the model
    address:
        Docker image address
    stateless:
        Flag, if true then model stateless, else statefull
    batch_size:
        Default batch size
    """

    name: str
    address: str
    stateless: bool
    batch_size: int


@dataclass(eq=False)
class RequestObject:
    """
    Format of input data.

    Parameters
    ----------
    uid:
        Uniq identifier of the request
    inputs:
        Input tensor, which will be processed
    source_id:
        Combination of adapter_id and user_id, need for result routing
    parameters:
        Meta information for processing
    model:
        Information about model
    """

    uid: str
    inputs: np.ndarray
    source_id: str
    parameters: dict
    model: ModelObject

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.uid == other.uid
            and np.array_equal(self.inputs, other.inputs)
            and self.parameters == other.parameters
            and self.model == other.model
        )


@dataclass(eq=False)
class BatchObject:
    """
    Format of BatchManager output data.

    Parameters
    ----------
    uid:
        Uniq identifier of the batch
    inputs:
        List of tensors, that will be processed.
    parameters:
        List of meta information for processing. Order is equal to order of inputs
    model:
        Information about model
    """

    uid: str
    inputs: List[np.ndarray]
    parameters: List[dict]
    model: ModelObject

    @property
    def size(self) -> int:
        "Actual batch size"
        return len(self.inputs)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.uid == other.uid
            and map(np.array_equal, zip(self.inputs, other.inputs))
            and self.parameters == other.parameters
            and self.model == other.model
        )


@dataclass
class BatchMapping:
    """
    Mapping between RequestObjects and BatchObject

    Parameters
    ----------
    batch_uid:
        Uniq identifier of batch
    request_object_uids:
        Uniq identifiers of RequestObjects
    source_ids:
        Ids of sourec
    """

    batch_uid: str
    request_object_uids: List[str]
    source_ids: List[str]

    def to_key_value(self) -> Tuple[bytes, bytes]:
        """
        Make key value tuple, that will be stored in LevelDB
        """
        key = self.batch_uid.encode("utf-8")
        value = json.dumps(
            dict(
                request_object_uids=self.request_object_uids, source_ids=self.source_ids
            )
        ).encode("utf-8")
        return key, value
