"""
This module is responsible for receiving batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import zmq  # type: ignore
import zmq.asyncio  # type: ignore

from loguru import logger

import src.data_models as dm
from src.batch_queue import InputBatchQueue

ctx = zmq.asyncio.Context()


def create_socket(config: dm.Config) -> zmq.asyncio.Socket:
    """
    Create async zeromq socket

    Parameters
    ----------
    config
        Config object, required field is a zmq_input_address
    """
    sock = ctx.socket(zmq.SUB)
    sock.bind(config.zmq_input_address)
    logger.info(f"Listen on {config.zmq_input_address}")
    sock.subscribe(b"")
    return sock


async def receive(sock: zmq.asyncio.Socket, input_batch_queue: InputBatchQueue):
    """
    Build an async iterable object. Infinite stream of RequestObject

    Parameters
    ----------
    sock:
        Socket is source of request_objects
    """
    while True:
        batch = await sock.recv_pyobj()
        if isinstance(batch, dm.MinimalBatchObject):
            await input_batch_queue.put(batch)
