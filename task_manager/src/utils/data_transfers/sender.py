"""
This module is responsible for sending data to model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq.asyncio  # type: ignore


class BaseSender:
    def __init__(self):
        pass

    def sync(self, sync_address, config):
        pass

    async def send(self, data):
        pass

    def close(self):
        pass


class Sender(BaseSender):
    """Opens zmq PUSH socket and sends RequestBatchObject"""

    def __init__(self, open_address, sync_address, config):
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, config.zmq_sndhwm)
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
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

    async def send(self, data):
        await self.zmq_socket.send_pyobj(data)

    def close(self):
        self.zmq_socket.close()
