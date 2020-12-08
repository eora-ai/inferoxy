"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import numpy as np  # type: ignore

from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

from shared_modules.data_objects import MinimalBatchObject, ModelObject, Status


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
    source_id: Optional[str]
    sender: Sender
    receiver: Receiver
    lock: bool


RequestBatch = MinimalBatchObject


@dataclass
class ResponseBatch(MinimalBatchObject):
    """
    Response batch object, add output and pictures
    """

    outputs: List[np.ndarray] = field(default_factory=list)
    pictures: List[Optional[np.ndarray]] = field(default_factory=list)

    @classmethod
    def from_request_batch_object(
        cls,
        batch: RequestBatch,
        outputs: List[np.ndarray],
        pictures: List[Optional[np.ndarray]],
        done_at: datetime,
    ):
        """
        Make Response Batch object from RequestBactch
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
