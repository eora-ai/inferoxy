"""
Data modules for listener component
"""

__author__ = "Andey Chertkov"
__email__ = "a.chertkov@eora.ru"


from dataclasses import dataclass

from pydantic import BaseModel

from shared_modules.data_objects import (
    RequestObject,
    RequestInfo,
    ModelObject,
    ResponseObject,
    BaseConfig,
)


class ZMQPythonAdapterConfig(BaseModel):
    listen_address: str
    send_address: str


class Config(BaseModel):
    """
    Config object
    """

    batch_manager_input_address: str
    debatch_manager_output_address: str
    model_storage_address: str

    zmq_python: ZMQPythonAdapterConfig
