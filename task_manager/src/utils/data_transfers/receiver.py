"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

import zmq
import sys

from loguru import logger

from shared_modules.data_objects import ResponseBatch


class Receiver:
    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, settings.ZMQ_SETTINGS.get("RCVHWM", 10))
        self.zmq_socket.setsockopt(
            zmq.RCVTIMEO, settings.ZMQ_SETTINGS.get("RCVTIMEO", 60000)
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

    async def receive(self) -> ResponseBatch:

        data = self.zmq_socket.recv_pyobj()
        try:
            minimal_batch = data.get("batch_object")
            outputs = data.get("outputs")
            pictures = data.get("pictures")

            if minimal_batch is None:
                sys.stdout.write("Minimal batch object is None")
                return None

            # Check that pictures is not None
            if pictures is not None and pictures.size != 0:
                response_outputs = [{"outputs": outputs, "pictures": pictures}]
            else:
                response_outputs = [{"outputs": outputs}]

            response = ResponseBatch.from_minimal_batch_object(
                batch=minimal_batch,
                outputs=response_outputs,
                source_id=minimal_batch.source_id,
                done_at=minimal_batch.done_at,
            )
            return response
        except KeyError:
            logger.error("No such key in dictionary")

    def close(self):
        self.zmq_socket.close()
