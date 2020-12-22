"""
This module is needed for send ResponseObject to somewhere
"""

import zmq  # type: ignore
import zmq.asyncio  # type: ignore

import src.data_models as dm

ctx = zmq.asyncio.Context()


def create_socket(config: dm.Config) -> zmq.asyncio.Socket:
    """
    Connect to `somewhere`
    """
    sock = ctx.socket(zmq.PUB)
    sock.connect(config.zmq_output_address)
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
