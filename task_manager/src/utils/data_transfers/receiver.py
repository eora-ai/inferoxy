"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq.asyncio

from loguru import logger

from shared_modules.data_objects import ResponseBatch


class BaseReceiver:
    def __init__(self):
        pass

    def sync(self, sync_address, config):
        pass

    async def receive(self):
        pass

    def close(self):
        pass


class Receiver(BaseReceiver):
    def __init__(self, open_address, sync_address, config):
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, config.zmq_rcvhwm)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
        self.zmq_socket.connect(open_address)
        self.sync(sync_address, config)

    def sync(self, sync_address, config):
        self.zmq_context = zmq.asyncio.Context()
        r = self.zmq_context.socket(zmq.REQ)
        r.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
        r.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
        r.connect(sync_address)
        r.send(b"Sync message")
        r.recv()
        r.close()

    async def receive(self) -> ResponseBatch:
        while True:
            data = await self.zmq_socket.recv_pyobj()
            response_batch = data.get("batch_object")
            break

        if response_batch is None:
            logger.warning("Response batch object is None")

        return response_batch

    def close(self):
        self.zmq_socket.close()
