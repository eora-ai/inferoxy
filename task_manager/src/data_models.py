"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import numpy as np  # type: ignore

from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

from shared_modules.data_objects import MinimalBatchObject, ModelObject


@dataclass
class Config:
    """
    Config of task manager
    """

    zmq_output_address: str
    zmq_input_address: str


@dataclass
class ModelInstance:
    """
    Store connection to the model
    """

    model: ModelObject
    sender: Sender
    receiver: Receiver
    lock: bool


class Status(Enum):
    """
    Enum that represents status of the batch processing
    """

    CREATED = "CREATED"
    STARTED = "STARTED"
    DONE = "DONE"
    SENT = "SENT"


@dataclass
class BatchWithTimesAndStatuses(MinimalBatchObject):
    """
    Data class which stores status and times of the batch
    """

    status: Status
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    done_at: Optional[datetime]
    queued_at: Optional[datetime]
    sent_at: Optional[datetime]


@dataclass
class RequestBatch(BatchWithTimesAndStatuses):
    """
    Request Batch Object
    """

    @classmethod
    def from_minimal_batch_object(cls, batch: MinimalBatchObject, **kwargs):
        """
        Make Request object from MinimalBatchObject
        """
        return cls(
            uid=batch.uid,
            inputs=batch.inputs,
            parameters=batch.parameters,
            model=batch.model,
            **kwargs
        )


@dataclass
class ResponseBatch(BatchWithTimesAndStatuses):
    """
    Response batch object, add output and pictures
    """

    outputs: List[np.ndarray]
    pictures: List[Optional[np.ndarray]]

    @classmethod
    def from_request_batch_object(
        cls,
        batch: RequestBatch,
        outputs: List[np.ndarray],
        pictures: List[Optional[np.ndarray]],
        done_at: datetime,
    ):
        """
        Make Request object from MinimalBatchObject
        """
        return cls(
            uid=batch.uid,
            inputs=batch.inputs,
            parameters=batch.parameters,
            model=batch.model,
            status=batch.status,
            created_at=batch.created_at,
            started_at=batch.started_at,
            done_at=done_at,
            queued_at=batch.queued_at,
            sent_at=batch.queued_at,
            pictures=pictures,
            outputs=outputs,
        )
