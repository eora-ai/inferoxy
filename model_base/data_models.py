__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


from dataclasses import dataclass

from pydantic_yaml import YamlModel     # type: ignore

from shared_modules.data_objects import (
    ResponseBatch,
    ResponseInfo,
    RequestInfo,
    ModelObject,
    MinimalBatchObject,
    MiniResponseBatch,
)


class ZMQConfig(YamlModel):
    """
    Config of base object (???)
    """

    zmq_sndhwm: int
    zmq_rcvhwm: int
    zmq_sndtimeo: int
    zmq_rcvtimeo: int
