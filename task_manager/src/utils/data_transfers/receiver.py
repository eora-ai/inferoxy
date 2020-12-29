"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq
from typing import Dict

import src.data_models as dm


class Receiver:
    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, settings.get("RCVHWM", 10))
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, settings.get("RCVTIMEO", 60000))
        self.zmq_socket.connect(open_address)
        # TODO Add sync

    async def sync(self):
        pass

    async def receive(self, data: Dict) -> dm.ResponseBatch:
        # TODO: Field: inputs, parameters, model, status - ???
        await dm.ResponseBatch(
            uid=data.get("uid"),
        )

    def close(self):
        self.zmq_socket.close()
