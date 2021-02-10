"""This module is responsible for receive message from zeromq ipc."""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import zmq  # type: ignore
import zmq.asyncio  # type: ignore

from typing import AsyncIterable

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


async def receive(sock: zmq.asyncio.Socket) -> AsyncIterable[dm.RequestObject]:
    """
    Build an async iterable object. Infinite stream of RequestObject

    Parameters
    ----------
    sock:
        Socket is source of request_objects
    """
    while True:
        request_object = await sock.recv_pyobj()
        yield request_object
