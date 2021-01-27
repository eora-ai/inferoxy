"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
from typing import AsyncIterator

import zmq.asyncio  # type: ignore
from loguru import logger

from shared_modules.data_objects import ResponseBatch, ZMQConfig


class BaseReceiver:
    def __init__(self):
        self.last_received_batch = time.time()
        pass

    def sync(self, sync_address, config):
        pass

    async def receive(self):
        pass

    def close(self):
        pass

    def get_time_of_last_received_batch(self):
        return self.last_received_batch


class Receiver(BaseReceiver):
    def __init__(self, open_address: str, sync_address: str, config: ZMQConfig):
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, config.rcvhwm)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, config.rcvtimeo)
        self.zmq_socket.connect(open_address)
        self.sync(sync_address, config)
        self.last_received_batch = time.time()

    def sync(self, sync_address: str, config: ZMQConfig):
        self.zmq_context = zmq.asyncio.Context()
        r = self.zmq_context.socket(zmq.REQ)
        r.setsockopt(zmq.SNDTIMEO, config.sndtimeo)
        r.setsockopt(zmq.RCVTIMEO, config.rcvtimeo)
        r.connect(sync_address)
        r.send(b"Sync message")
        r.recv()
        r.close()

    async def receive(self) -> AsyncIterator[ResponseBatch]:
        while True:
            response_batch = await self.zmq_socket.recv_pyobj()

            if response_batch is None:
                logger.warning("Response batch object is None")

            self.last_received_batch = time.time()

            yield response_batch

    def close(self):
        self.zmq_socket.close()

    def get_time_of_last_received_batch(self):
        return self.last_received_batch
