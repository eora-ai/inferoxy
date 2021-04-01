"""
Data object definitions
"""

from typing import Optional

from pydantic_yaml import YamlModel     # type: ignore

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


class Config(YamlModel):
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

    zmq_input_address: Optional[str] = None
    zmq_output_address: Optional[str] = ""
    db_file: Optional[str] = None
    create_db_file: Optional[bool] = None
    send_batch_mapping_timeout: Optional[float] = None
