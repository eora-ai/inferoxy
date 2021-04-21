__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import List

import numpy as np  # type: ignore
import zmq  # type: ignore
import zmq.asyncio  # type: ignore

from shared_modules.utils import uuid4_string_generator
import shared_modules.data_objects as dm

generator = uuid4_string_generator()


async def get_model(
    slug: str, model_storage_address: str, ctx: zmq.asyncio.Context
) -> dm.ModelObject:
    """
    Get model object using model_storage

    Parameters
    ----------
    slug:
        Slug of the model
    model_storage_address:
        ZMQ address of model storage
    ctx:
        ZMQ context that will be used to create ZMQ socket
    """
    sock = ctx.socket(zmq.REQ)
    sock.connect(model_storage_address)
    await sock.send_string(slug)
    model_object = await sock.recv_pyobj()
    sock.close()
    del sock
    return model_object


async def input_to_requests_object(
    request_model: dm.RequestModel,
    model_storage_address: str,
    topic: str = "",
    ctx: zmq.asyncio.Context = None,
) -> List[dm.RequestObject]:
    """
    Transform request model into list of request objects

    Parameters
    ----------
    request_model:
        Request model that will be transformed into `request_object`
    model_storage_address:
        ZMQ address of model storage
    topic:
        Topic that will be add to the source_id, such that `debatch_manager`
        will know where is a distenation of response batches.
    ctx:
        ZMQ context that will be used to create ZMQ socket for connecting to model_storage_address
    """
    if ctx is None:
        ctx = zmq.asyncio.Context.instance()
    inputs = request_model.inputs
    request_objects = []

    for input_model in inputs:
        request_info = convert_input_model(input_model)
        model_obj = await get_model(request_model.model, model_storage_address, ctx)
        request_object = dm.RequestObject(
            uid=next(generator),
            source_id=topic + ":" + request_model.source_id,
            request_info=request_info,
            model=model_obj,
        )
        request_objects.append(request_object)

    return request_objects


def convert_input_model(input_model: dm.InputModel) -> dm.RequestInfo:
    """
    Convert InputModel into RequestInfo
    """
    if isinstance(input_model.data, np.ndarray):
        array = input_model.data
    else:
        array = np.array(input_model.data)
    if input_model.datatype:
        array.astype(input_model.datatype.value)
    if input_model.shape:
        array.astype(input_model.shape)

    return dm.RequestInfo(input=array, parameters=input_model.parameters)


def response_object_to_output(
    response_object: dm.ResponseObject, keep_numpy: bool = False
) -> dm.ResponseModel:
    """
    Convert response object intou output model
    """

    output_models = None
    if not response_object.error and response_object.response_info:

        response_info = response_object.response_info
        shape = None
        datatype = None
        data = None
        if response_info.picture:
            shape = response_info.picture.shape
            datatype = str(response_info.picture.dtype)
            if not keep_numpy:
                data = response_info.picture.reshape((-1,))
            else:
                data = response_info.picture
        output_models = [
            dm.OutputModel(
                shape=shape,
                datatype=datatype,
                data=data,
                parameters=response_info.parameters,
                output=response_info.output,
            )
        ]

    response_model = dm.ResponseModel(
        model=response_object.model.name,
        outputs=output_models,
        error=response_object.error,
        source_id=response_object.source_id,
    )

    return response_model


def get_batch_manager_socket(ctx: zmq.asyncio.Context, address: str) -> zmq.Socket:
    socket = ctx.socket(zmq.PUSH)
    socket.connect(address)
    return socket


def get_debatch_manager_socket(
    ctx: zmq.asyncio.Context, address: str, topic: str
) -> zmq.Socket:
    socket = ctx.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, topic.encode("utf-8"))
    socket.connect(address)
    return socket
