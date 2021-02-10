"""
This is shared data objects.
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import json
import numpy as np  # type: ignore

from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Type, NewType


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
    run_on_gpu: bool = False

    def __hash__(self):
        return hash((self.name, self.address))


@dataclass
class RequestInfo:
    input: np.ndarray
    parameters: dict

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.inputs == other.inputs and self.parameters == other.parameters


@dataclass
class ResponseInfo:
    output: np.ndarray
    parameters: dict
    picture: Optional[np.ndarray]

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return np.array_equal(self.output, other.output) and np.array_equal(
            self.picture, other.picture
        )


@dataclass
class RequestObject:
    """
    Format of input data.

    Parameters
    ----------
    uid:
        Uniq identifier of the request
    source_id:
        Combination of adapter_id and user_id, need for result routing
    model:
        Information about model
    request_info:
        RequestInfo is a payload of the request
    """

    uid: str
    source_id: str
    request_info: RequestInfo
    model: ModelObject


@dataclass
class ResponseObject:
    """
    Format of ouput data.

    Parameters:
    __________
    uid:
        Uniq identifier of the request
    model:
        Inforamtion about model
    response_info:
        ResponseInfo is a payload of the response
    error:
        String error, that will be displayed to user
    """

    uid: str
    model: ModelObject
    response_info: Optional[ResponseInfo]
    error: Optional[str]
    source_id: str


class Status(Enum):
    """
    Enum that represents status of the batch processing
    """

    CREATING = "CREATING"
    CREATED = "CREATED"
    IN_QUEUE = "IN_QUEUE"
    SENT_TO_MODEL = "SENT_TO_MODEL"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    DONE = "DONE"


@dataclass(eq=False)
class MinimalBatchObject:
    """
    Format of BatchManager output data.
    This object will be sent over the zmq output socket

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
    requests_info: List[RequestInfo]
    model: ModelObject
    status: Status = Status.CREATING
    source_id: Optional[str] = None
    created_at: Optional[datetime] = None
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    done_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    debached_at: Optional[datetime] = None

    @property
    def size(self) -> int:
        "Actual batch size"
        return len(self.requests_info)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return (
            self.uid == other.uid
            and self.model == other.model
            and self.requests_info == other.requests_info
            and self.source_id == other.source_id
            and self.status == other.status
        )

    def __hash__(self):
        return hash(self.uid)


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

    @classmethod
    def from_key_value(cls, data: Tuple[bytes, bytes]):
        key = data[0].decode("utf-8")
        value = json.loads(data[1])
        request_object_uids = value["request_object_uids"]
        source_ids = value["source_ids"]

        return cls(
            batch_uid=key,
            request_object_uids=request_object_uids,
            source_ids=source_ids,
        )


@dataclass
class ResponseBatch(MinimalBatchObject):
    """
    Response batch object, add output and pictures
    """

    responses_info: Optional[List[ResponseInfo]] = None
    error: Optional[str] = None

    @classmethod
    def from_minimal_batch_object(
        cls,
        batch: MinimalBatchObject,
        error: Optional[str] = None,
        responses_info: Optional[List[ResponseInfo]] = None,
    ):
        """
        Make Response Batch object from RequestBactch
        """
        return cls(
            uid=batch.uid,
            requests_info=batch.requests_info,
            model=batch.model,
            status=batch.status,
            created_at=batch.created_at,
            started_at=batch.started_at,
            done_at=batch.done_at,
            queued_at=batch.queued_at,
            sent_at=batch.queued_at,
            responses_info=responses_info,
            error=error,
        )

    def __hash__(self):
        return hash(self.uid)


class BaseConfig:
    """
    Generic type of config
    """


@dataclass
class ZMQConfig(BaseConfig):
    """
    Config for ZMQ senders receivers
    """

    sndhwm: int
    rcvhwm: int
    sndtimeo: int
    rcvtimeo: int


@dataclass
class PortConfig(BaseConfig):
    """
    Config for sender/receiver ports
    """

    sender_open_addr: int
    sender_sync_addr: int
    receiver_open_addr: int
    receiver_sync_addr: int
