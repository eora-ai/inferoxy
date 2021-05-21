"""
Useful functions for `grpc_bridge`
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Any, Dict
import json

import pydantic
from loguru import logger

import src.data_models as dm


def grpc_model_into_pydantic_model(
    infer_request: dm.InferRequest,
) -> dm.RequestModel:
    """
    Convert grpc model into pydantic model
    """
    data = infer_request.message_to_dict(including_default_value_fields=False)
    data["inputs"] = list(map(to_pydantic_inputs, data["inputs"]))
    try:
        return dm.RequestModel(**data)
    except pydantic.ValidationError as exc:
        logger.exception(exc)
        raise exc


def to_pydantic_inputs(grpc_input: dict) -> dict:
    """
    Convert grpc inputs field into pydantic inputs
    """
    result = {
        "shape": grpc_input["shape"],
        "datatype": grpc_input["datatype"],
        "parameters": {},
        "data": [],
    }

    for key in grpc_input["parameters"]:
        parameters_data_key = next(iter(grpc_input["parameters"][key].keys()))
        result["parameters"][key] = grpc_input["parameters"][key][parameters_data_key]
    data_key = next(iter(grpc_input["data"].keys()))
    result["data"] = grpc_input["data"][data_key]
    return result


def response_model_to_infer_result(response_model: dm.ResponseModel) -> dm.InferResult:
    """
    Convert response pydantic model into InferResult
    """
    outputs = list(map(output_model_to_output_infer, response_model.outputs))
    return dm.InferResult(
        source_id=response_model.source_id, model=response_model.model, outputs=outputs
    )


def output_model_to_output_infer(output_model: dm.OutputModel) -> dm.OutputInfer:
    """
    Convert output model into output infer
    """

    output_json_encoded = json.dumps(output_model.output)

    def __define_name(value: Any) -> Dict[str, Any]:
        if isinstance(value, str):
            return {"string_param": value}
        if isinstance(value, bool):
            return {"bool_param": value}
        if isinstance(value, int):
            return {"int_param": value}
        if isinstance(value, float):
            return {"float_param": value}
        return {"string_param": str(value)}

    parameters = {
        k: dm.ParameterMessage(**__define_name(v))
        for k, v in output_model.parameters.items()
    }

    return dm.OutputInfer(
        shape=output_model.shape,
        datatype=output_model.datatype,
        data=dm.InferData(payload_int=output_model.data),
        output=output_json_encoded,
        parameters=parameters,
        error=output_model.error,
    )
