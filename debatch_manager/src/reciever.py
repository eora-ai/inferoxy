"""This module is responsible for receive message from zeromq ipc."""
from typing import AsyncIterable

import zmq
import zmq.asyncio

import src.data_models as dm

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
    sock.subscribe(b"")
    return sock


async def receive(
    sock: zmq.asyncio.Socket
) -> AsyncIterable[dm.ResponseBatch]:
    """
    Build an async iterable object. Infinite stream of ResponseBatch

    Parameters
    ----------
    sock:
        Socket is source of response_batch
    """
    while True:
        response_batch = await sock.recv_pyobj()
        yield response_batch
