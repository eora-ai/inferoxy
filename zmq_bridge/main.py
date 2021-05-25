"""
Entrypoint of the zmq bridge
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import sys
import argparse
import asyncio

import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger
import pydantic

from shared_modules import bridge_utils, parse_config
from shared_modules.utils import recreate_logger

import src.data_models as dm


async def receive_input(
    input_socket: zmq.Socket, output_socket: zmq.Socket, config: dm.Config
):
    """
    Receive input from socket
    """
    while True:
        input_dict = await input_socket.recv_pyobj()
        logger.info("Something received 🚀")

        try:
            request_model = dm.RequestModel(**input_dict)
        except pydantic.ValidationError as exc:
            logger.exception(exc)
            continue

        context = zmq.asyncio.Context.instance()

        requests_object = await bridge_utils.input_to_requests_object(
            request_model, config.model_storage_address, topic="zmq", ctx=context
        )
        for request_object in requests_object:
            await output_socket.send_pyobj(request_object)


async def receive_output(input_socket: zmq.Socket, output_socket: zmq.Socket):
    """
    Receive info from socket subscribe to output
    """
    while True:
        result_object: dm.ResponseObject = await input_socket.recv_pyobj()
        logger.info(f"Processed object with {result_object.source_id=}")
        try:
            output_model: dm.ResponseModel = bridge_utils.response_objects_to_output(
                [result_object], keep_numpy=True
            )
        except pydantic.ValidationError as exc:
            logger.exception(exc)
            continue
        await output_socket.send_string(result_object.source_id, zmq.SNDMORE)
        await output_socket.send_pyobj(output_model.dict())


async def pipeline(config: dm.Config):
    """
    make receive from input async task
    make receive from debatch manager async task
    make send to output queue async task
    make sending to batch manager async task
    Pydantic -> request object
    Send request obj to batch manager
    Receive response object from debatch manger
    Response object -> Pydantic
    """
    ctx = zmq.asyncio.Context()
    input_socket = ctx.socket(zmq.PULL)
    input_socket.bind(config.listen_address)
    output_socket = ctx.socket(zmq.ROUTER)
    output_socket.bind(config.send_address)

    batch_manager_socket = bridge_utils.get_batch_manager_socket(
        ctx, config.batch_manager_address
    )
    debatch_manager_socket = bridge_utils.get_debatch_manager_socket(
        ctx, address=config.debatch_manager_address, topic="zmq"
    )
    await asyncio.wait(
        [
            receive_input(input_socket, batch_manager_socket, config),
            receive_output(debatch_manager_socket, output_socket),
        ]
    )


def main():
    log_level = os.getenv("LOGGING_LEVEL")
    recreate_logger(log_level, "ZMQ_BRIDGE")

    logger.info("Read config file")
    parser = argparse.ArgumentParser(description="Listener process")
    parser.add_argument(
        "--config",
        type=str,
        help="Config path",
        default="/etc/inferoxy/zmq_bridge.yaml",
    )
    args = parser.parse_args()
    config = parse_config.read_config_with_env(
        dm.Config, args.config, env_prefix="zmq_bridge"
    )
    asyncio.run(pipeline(config))


if __name__ == "__main__":
    main()
