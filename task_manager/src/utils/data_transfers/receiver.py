"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq.asyncio
import sys

from loguru import logger

from shared_modules.data_objects import ResponseBatch


class Receiver:
    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, settings.ZMQ_SETTINGS.get("RCVHWM", 10))
        self.zmq_socket.setsockopt(
            zmq.RCVTIMEO, settings.ZMQ_SETTINGS.get("RCVTIMEO", 60000)
        )
        self.zmq_socket.connect(open_address)
        self.sync(sync_address, settings)

    def sync(self, sync_address, settings):
        self.zmq_context = zmq.asyncio.Context()
        r = self.zmq_context.socket(zmq.REQ)
        r.setsockopt(zmq.SNDTIMEO, settings.ZMQ_SETTINGS.get("SNDTIMEO", 60000))
        r.setsockopt(zmq.RCVTIMEO, settings.ZMQ_SETTINGS.get("RCVTIMEO", 60000))
        r.connect(sync_address)
        r.send(b"Sync message")
        sys.stdout.write("Send request to model\n")
        r.recv()
        sys.stdout.write("Model is ready\n")
        sys.stdout.flush()
        r.close()

    async def receive(self) -> ResponseBatch:
        while True:
            sys.stdout.write("Parse received data\n")
            data = await self.zmq_socket.recv_pyobj()
            response_batch = data.get("batch_object")
            break

        if response_batch is None:
            logger.info("Response batch object is None")

        sys.stdout.write("\n")
        return response_batch

    def close(self):
        self.zmq_socket.close()
