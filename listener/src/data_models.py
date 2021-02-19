"""
Data modules for listener component
"""

__author__ = "Andey Chertkov"
__email__ = "a.chertkov@eora.ru"


from dataclasses import dataclass

from shared_modules.data_objects import (
    RequestObject,
    RequestInfo,
    ModelObject,
    ResponseObject,
    BaseConfig,
)


@dataclass
class ZMQPythonAdapterConfig(BaseConfig):
    listen_address: str
    send_address: str


@dataclass
class Config(BaseConfig):
    """
    Config object
    """

    batch_manager_input_address: str
    debatch_manager_output_address: str
    model_storage_address: str

    zmq_python: ZMQPythonAdapterConfig

    @classmethod
    def from_dict(cls, config_dict):
        """
        Make Configobject from the
        """
        zmq_python_config = ZMQPythonAdapterConfig(**config_dict.pop("zmq_python"))
        return cls(zmq_python=zmq_python_config, **config_dict)