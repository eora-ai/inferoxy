"""
This module is needed for send ResponseObject to somewhere
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import zmq  # type: ignore
import zmq.asyncio  # type: ignore

import src.data_models as dm

ctx = zmq.asyncio.Context()


def create_socket(config: dm.Config) -> zmq.asyncio.Socket:
    """
    bind socket
    """
    sock = ctx.socket(zmq.PUSH)
    sock.bind(config.zmq_output_address)
    return sock


async def send(sock: zmq.asyncio.Socket, response_object: dm.ResponseObject):
    """
    Sending to `somewhere` response object

    Parameters
    ----------
    sock:
        Socket is destination of response objects
    """
    await sock.send_pyobj(response_object)
