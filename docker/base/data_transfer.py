import sys

import zmq
import time


class Sender:
    """Opens zmq PUSH socket and sends python obj."""

    def __init__(self, open_address, sync_address, settings):

        print("SENDER OPEN ADDRESS: ", open_address)
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, settings.get("SNDHWM", 10))
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, settings.get("SNDTIMEO", 60000))
        self.zmq_socket.bind(open_address)
        self._sync(sync_address, settings)

    def _sync(self, sync_address, settings):
        ctx = zmq.Context.instance()
        s = ctx.socket(zmq.REP)
        s.setsockopt(zmq.SNDTIMEO, settings.get("SNDTIMEO", 60000))
        s.setsockopt(zmq.RCVTIMEO, settings.get("RCVTIMEO", 60000))
        s.bind(sync_address)
        sys.stdout.write("Waiting for receiver to connect...\n")
        s.recv()
        time.sleep(1)
        sys.stdout.write("Receiver connected\n")
        sys.stdout.flush()
        s.send(b"GO")
        s.close()

    def send(self, data):
        self.zmq_socket.send_pyobj(data)

    def close(self):
        self.zmq_socket.close()


class Receiver:
    """Opens zmq PULL socket and receives python obj."""

    def __init__(self, open_address, sync_address, settings):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, settings.get("RCVHWM", 10))
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, settings.get("RCVTIMEO", 60000))
        self.zmq_socket.bind(open_address)
        self._sync(sync_address, settings)

    def _sync(self, sync_address, settings):
        ctx = zmq.Context.instance()
        s = ctx.socket(zmq.REP)
        s.setsockopt(zmq.SNDTIMEO, settings.get("SNDTIMEO", 60000))
        s.setsockopt(zmq.RCVTIMEO, settings.get("RCVTIMEO", 60000))
        s.bind(sync_address)
        sys.stdout.write("Waiting for sender to connect...\n")
        s.recv()
        time.sleep(1)
        sys.stdout.write("Sender connected\n")
        sys.stdout.flush()
        s.send(b"GO")
        s.close()

    def receive(self):
        data = self.zmq_socket.recv_pyobj()
        return data

    def close(self):
        self.zmq_socket.close()
