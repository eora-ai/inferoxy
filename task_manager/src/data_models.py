"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from dataclasses import dataclass
from typing import List, Optional


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
    gpu_all: List[int]


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
    num_gpu: Optional[int] = None


RequestBatch = MinimalBatchObject
