"""This module is responsible for receive message from zeromq ipc."""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


from typing import AsyncIterable

import zmq  # type: ignore
import zmq.asyncio  # type: ignore

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
    sock = ctx.socket(zmq.PULL)
    sock.bind(config.zmq_input_address)
    return sock


async def receive(sock: zmq.asyncio.Socket) -> AsyncIterable[dm.ResponseBatch]:
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
