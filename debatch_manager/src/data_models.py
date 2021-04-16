"""
Data object definitions
"""

from pydantic import BaseModel

from shared_modules.data_objects import (
    Status,
    ModelObject,
    RequestObject,
    MinimalBatchObject,
    BatchMapping,
    MiniResponseBatch,
    ResponseObject,
    ResponseBatch,
    RequestInfo,
    ResponseInfo,
)


class Config(BaseModel):
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
    """

    zmq_input_address: str
    zmq_output_address: str
    db_file: str
    create_db_file: bool
    send_batch_mapping_timeout: float
