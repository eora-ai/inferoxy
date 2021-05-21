"""
Here implemented inference service
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Union, Type
from uuid import uuid4
import asyncio

from grpcalchemy import Server, Context, grpcmethod
from grpcalchemy.config import DefaultConfig
import zmq

import pydantic
from loguru import logger

import src.data_models as dm
from src.utils import grpc_model_into_pydantic_model, response_model_to_infer_result
from shared_modules.bridge_utils import (
    input_to_requests_object,
    get_batch_manager_socket,
    get_debatch_manager_socket,
    response_objects_to_output,
)

ctx = zmq.Context()


def get_inference_service(config: dm.Config) -> Type:
    class InferenceService(Server):
        @grpcmethod
        def Infer(self, request: dm.InferRequest, context: Context) -> dm.InferResult:
            logger.info("Something received 🚀")

            # Build request object out of grpc message
            pydantic_model = grpc_model_into_pydantic_model(request)
            topic = f"grpc_{uuid4()}"
            request_object_aw = input_to_requests_object(
                pydantic_model, config.model_storage_address, topic=topic
            )
            request_object = asyncio.new_event_loop().run_until_complete(
                request_object_aw
            )[0]
            logger.debug(f"Built request object: {request_object}")

            # Send request object into batch manager

            batch_channel = get_batch_manager_socket(ctx, config.batch_manager_address)
            batch_channel.send_pyobj(request_object)

            debatch_channel = get_debatch_manager_socket(
                ctx, config.debatch_manager_address, topic
            )
            response_object: dm.ResponseObject = debatch_channel.recv_pyobj()
            response_model = response_objects_to_output([response_object])
            infer_result = response_model_to_infer_result(response_model)
            return infer_result

    return InferenceService
