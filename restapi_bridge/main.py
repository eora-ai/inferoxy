import os
from uuid import uuid4

from loguru import logger
from fastapi import FastAPI, Depends
import zmq.asyncio  # type: ignore

from shared_modules.bridge_utils import (
    input_to_requests_object,
    get_batch_manager_socket,
    get_debatch_manager_socket,
    response_objects_to_output,
)
from shared_modules.parse_config import read_config_with_env
from shared_modules.utils import recreate_logger

import src.data_models as dm

log_level = os.getenv("LOGGING_LEVEL")
recreate_logger(log_level, "RESTAPI_BRIDGE")


app = FastAPI()
config = read_config_with_env(
    config_type=dm.Config,
    config_path="/etc/inferoxy/restapi_bridge.yaml",
    env_prefix="restapi",
)


async def get_context():
    ctx = zmq.asyncio.Context()
    yield ctx


@app.post("/infer")
async def infer(
    request: dm.RequestModel,
    ctx: zmq.asyncio.Context = Depends(get_context),
):
    topic_uid = f"restapi-{uuid4()}"
    request_objects = await input_to_requests_object(
        request, config.model_storage_address, topic_uid, ctx
    )

    results_len = len(request_objects)
    batch_socket: zmq.Socket = get_batch_manager_socket(
        ctx, config.batch_manager_address
    )
    output_socket: zmq.Socket = get_debatch_manager_socket(
        ctx, config.debatch_manager_address, topic=topic_uid
    )

    for request_object in request_objects:
        batch_socket.send_pyobj(request_object)

    response_objects = []
    for _ in range(results_len):
        response_object = await output_socket.recv_pyobj()
        response_objects.append(response_object)
    response_model = response_objects_to_output(response_objects)
    return response_model
