"""
This module is responsible for sending data to model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq
import sys


class Sender:
    """Opens zmq PUSH socket and sends RequestBatchObject"""

    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, settings.ZMQ_SETTINGS.get("SNDHWM", 10))
        self.zmq_socket.setsockopt(
            zmq.SNDTIMEO, settings.ZMQ_SETTINGS.get("SNDTIMEO", 60000)
        )
        self.zmq_socket.connect(open_address)
        self.sync(sync_address, settings)

    def sync(self, sync_address, settings):
        ctx = zmq.Context.instance()
        r = ctx.socket(zmq.REQ)
        r.setsockopt(zmq.SNDTIMEO, settings.ZMQ_SETTINGS.get("SNDTIMEO", 60000))
        r.setsockopt(zmq.RCVTIMEO, settings.ZMQ_SETTINGS.get("RCVTIMEO", 60000))
        r.connect(sync_address)
        r.send(b"Sync message")
        sys.stdout.write("Send request to model\n")
        r.recv()
        sys.stdout.write("Model is ready\n")
        sys.stdout.flush()
        r.close()

    async def send(self, minimal_batch_obj):
        data = {"batch_object": minimal_batch_obj}
        self.zmq_socket.send_pyobj(data)

    def close(self):
        self.zmq_socket.close()
