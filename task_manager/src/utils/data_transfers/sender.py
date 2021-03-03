"""
This module is responsible for sending data to model instance
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
from loguru import logger

import zmq.asyncio  # type: ignore


class BaseSender:
    def __init__(self):
        self.last_sent_batch = time.time()

    async def send(self, data):
        pass

    def close(self):
        pass

    def get_time_of_last_sent_batch(self):
        return self.last_sent_batch


class Sender(BaseSender):
    """Opens zmq PUSH socket and sends RequestBatchObject"""

    def __init__(self, open_address, context, config):
        super().__init__()
        self.zmq_context = context
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, config.sndhwm)
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, config.sndtimeo)
        self.zmq_socket.connect(open_address)
        self.last_sent_batch = time.time()

    async def send(self, data):
        await self.zmq_socket.send_pyobj(data)
        self.last_sent_batch = time.time()

    def close(self):
        self.zmq_socket.close()

    def get_time_of_last_sent_batch(self):
        return self.last_sent_batch
