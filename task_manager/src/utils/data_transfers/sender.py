"""
This module is responsible for sending data to model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq
import sys

import src.data_models as dm


class Sender:
    """Opens zmq PUSH socket and sends RequestBatchObject"""

    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.smq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, settings.get("SNDHWM", 10))
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, settings.get("SNDTIMEO", 60000))
        self.zmq_socket.connect(open_address)
        # TODO Add sync

    async def sync(self, sync_address, settings):
        # TODO: how to make it async

        ctx = zmq.Context.instance()
        r = ctx.socket(zmq.REQ)
        r.setsockopt(zmq.SNDTIMEO, settings.get("SNDTIMEO", 60000))
        r.setsockopt(zmq.RCVTIMEO, settings.get("RCVTIMEO", 60000))
        r.connect(sync_address)
        sys.stdout.write("Connect to model\n")
        await r.send()
        sys.stdout.write("Send request to model\n")
        r.recv()
        sys.stdout.write("Model is ready\n")
        sys.stdout.flush()
        r.close()

    async def send(self, request_obj: dm.RequestObject):
        uid_request_obj = request_obj.uid
        inputs_request_obj = request_obj.inputs
        parameters_request_obj = request_obj.parameters

        data = {
            "uid": uid_request_obj,
            "inputs": inputs_request_obj,
            "parameters": parameters_request_obj,
        }
        await self.zmq_socket.send_pyobj(data)

    def close(self):
        self.zmq_socket.close()
