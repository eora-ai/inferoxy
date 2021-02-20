"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
from typing import Optional

import zmq  # type: ignore
import zmq.asyncio  # type: ignore
from loguru import logger

from shared_modules.data_objects import ResponseBatch, ZMQConfig


class BaseReceiver:
    def __init__(self):
        self.last_received_batch = time.time()
        self.model_instance = None

    async def receive(self):
        pass

    def close(self):
        pass

    def get_time_of_last_received_batch(self):
        return self.last_received_batch

    def set_model_instance(self, model_instance):
        self.model_instance = model_instance

    def get_model_instance(self):
        if self.model_instance is None:
            raise ValueError("ModelInstance is None")
        return self.model_instance


class Receiver(BaseReceiver):
    def __init__(
        self,
        open_address: str,
        context: zmq.asyncio.Context,
        config: ZMQConfig,
    ):
        super().__init__()
        self.zmq_context = context  # zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, config.rcvhwm)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, config.rcvtimeo)
        self.zmq_socket.connect(open_address)

    async def receive(self) -> Optional[ResponseBatch]:
        try:
            if not self.zmq_socket.closed:
                batch = await self.zmq_socket.recv_pyobj()
                self.last_received_batch = time.time()
                return batch
            return
        except zmq.Again:
            return

    def close(self):
        self.zmq_socket.close()
