"""
Data models of grpc bridge
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from dataclasses import dataclass
from typing import List, Any, Optional

from pydantic import BaseModel

from grpcalchemy.orm import (
    Message,
    MapField,
    ReferenceField,
    MapField,
    StringField,
    Repeated,
    BaseField,
)

from shared_modules.data_objects import (
    RequestModel,
    InputModel,
    DataTypes,
    ResponseObject,
    ResponseModel,
    OutputModel,
)


class Config(BaseModel):
    host: str = "0.0.0.0"
    port: int = 50051
    batch_manager_address: str
    debatch_manager_address: str
    model_storage_address: str


class ParameterMessage(Message):
    bool_param: bool
    int_param: int
    float_param: float
    string_param: str


class Int64Field(BaseField):
    __type_name__ = "int64"



class UintField(BaseField):
    __type_name__ = "uint32"


class Uint64Field(BaseField):
    __type_name__ = "uint64"


class InferData(Message):

    payload_int: Repeated[int]
    payload_int64: Repeated[Int64Field]

    payload_uint: Repeated[UintField]
    payload_uint64: Repeated[Uint64Field]

    payload_float: Repeated[float]


class InputInferRequest(Message):
    shape: Repeated[int]
    datatype: str
    data = ReferenceField(InferData())
    parameters = MapField(StringField(), ReferenceField(ParameterMessage()))


class InferRequest(Message):
    source_id: str
    model: str
    inputs: Repeated[InputInferRequest]


class OutputInfer(Message):
    shape: Repeated[int]
    datatype: str
    data = ReferenceField(InferData())
    output: str  # JSON encode string
    parameters = MapField(StringField(), ReferenceField(ParameterMessage()))
    error: str


class InferResult(Message):
    model: str
    source_id: str
    outputs: Repeated[OutputInfer]
