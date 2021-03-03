"""
This module is responsible for sending ResponseBatch
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger

import src.data_models as dm
from src.batch_queue import OutputBatchQueue


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
    logger.info(f"Send results on {config.zmq_output_address}")
    return sock


async def send(sock: zmq.asyncio.Socket, output_batch_queue: OutputBatchQueue):
    """
    Sending to TaskManager batch

    Parameters
    ----------
    sock:
        Socket is destination of batches
    """
    while True:
        batch = await output_batch_queue.get()
        logger.debug(f"Try to sent result batch {batch.uid=}")
        await sock.send_pyobj(batch)
        logger.debug(f"Batch {batch.uid=} sent")
