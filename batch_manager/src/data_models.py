"""
Data object definitions
"""
__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List
from dataclasses import dataclass, field

from shared_modules.data_objects import (
    Status,
    ModelObject,
    RequestObject,
    MinimalBatchObject,
    BatchMapping,
    RequestInfo,
)


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
    db_file:
        File path to leveldb
    create_db_file:
        Create db file if file doesnot exists
    send_batch_timeout:
        How much time builder will be sleep before sending
    """

    zmq_input_address: str
    zmq_output_address: str
    db_file: str
    create_db_file: bool
    send_batch_timeout: float


@dataclass(eq=False)
class BatchObject(MinimalBatchObject):
    """
    Format of BatchManager output data. This object stores more information that minimal.

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
    source_id:
        Source id if model is stateful, if stateless source_id=""
    request_objects:
        List of RequestObject
    """

    request_objects: List[RequestObject] = field(default_factory=list)

    def serialize(self) -> MinimalBatchObject:
        """
        Serialize BatchObject to MinimalBatchObject, that will sent over zeromq
        """
        return MinimalBatchObject(
            uid=self.uid,
            requests_info=self.requests_info,
            model=self.model,
            source_id=self.source_id,
            status=self.status,
            created_at=self.created_at,
        )

    def __eq__(self, other):
        return super().__eq__(other) and self.request_objects == other.request_objects


@dataclass
class Batches:
    """
    This dataclass is needed for store list of batches
    """

    batches: List[BatchObject]

    def __iter__(self):
        return iter(self.batches)

    def __getitem__(self, i):
        return self.batches[i]

    def add(self, batch: BatchObject):
        """
        Add element to batches list
        """
        if not isinstance(batch, BatchObject):
            raise ValueError("Batch must be BatchObject")
        self.batches += [batch]

    def set(self, batches: List[BatchObject]):
        """
        Set to internal batches
        """
        self.batches = batches
