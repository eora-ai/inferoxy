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

from shared_modules.data_objects import (
    ModelObject,
    MinimalBatchObject,
    Status,
    ResponseBatch,
)


@dataclass
class Config:
    """
    Config of task manager
    """

    zmq_output_address: str
    zmq_input_address: str
    docker_registry: str
    docker_login: str
    docker_password: str


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
    container_name: str


RequestBatch = MinimalBatchObject
