"""
This module is needed for send batch to TaskManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import zmq  # type: ignore
import zmq.asyncio  # type: ignore

import src.data_models as dm


ctx = zmq.asyncio.Context()


def create_socket(config: dm.Config) -> zmq.asyncio.Socket:
    """
    Connect to TaskManager

    Parameters
    ----------
    config:
        Config object, required field is a zmq_output_address
    """
    sock = ctx.socket(zmq.PUSH)
    sock.connect(config.zmq_output_address)
    return sock


async def send(sock: zmq.asyncio.Socket, batch: dm.BatchObject):
    """
    Sending to TaskManager batch

    Parameters
    ----------
    sock:
        Socket is destination of batches
    """
    await sock.send_pyobj(batch.serialize())
