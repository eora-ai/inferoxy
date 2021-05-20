"""
Tests for grpc to pydantic function
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from src.utils import to_pydantic_inputs
import src.data_models as dm


def test_grpc_to_pydantic():
    infer_request = {
        "shape": [1],
        "datatype": "uint8",
        "data": {"payload_int": [1, 2, 3, 4, 5]},
        "parameters": {"end": {"bool_param": True}},
    }
    result = to_pydantic_inputs(infer_request)
    assert result == {
        "shape": [1],
        "datatype": "uint8",
        "data": [1, 2, 3, 4, 5],
        "parameters": {"end": True},
    }


def test_grpc_to_pydantic_complicated_parameters():
    infer_request = {
        "shape": [1],
        "datatype": "uint8",
        "data": {"payload_float": [1, 2, 3, 4, 5]},
        "parameters": {"end": {"bool_param": False, "int_param": 10}},
    }
    result = to_pydantic_inputs(infer_request)
    assert result == {
        "shape": [1],
        "datatype": "uint8",
        "data": [1, 2, 3, 4, 5],
        "parameters": {"end": False},
    }
