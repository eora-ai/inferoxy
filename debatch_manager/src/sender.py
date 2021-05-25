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
    sock = ctx.socket(zmq.ROUTER)
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
    topic, source_id, *_ = response_object.source_id.split(":")
    response_object.source_id = source_id
    await sock.send_string(topic, zmq.SNDMORE)
    await sock.send_pyobj(response_object)
