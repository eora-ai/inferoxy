import sys
import zmq
import time


class Sender:
    """Opens zmq PUSH socket and sends python obj."""

    def __init__(self, open_address, sync_address, config):

        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, config.zmq_sndhwm)
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
        self.zmq_socket.bind(open_address)
        self._sync(sync_address, config)

    def _sync(self, sync_address, config):
        ctx = zmq.Context.instance()
        s = ctx.socket(zmq.REP)
        s.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
        s.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
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

    def __init__(self, open_address, sync_address, config):

        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, config.zmq_rcvhwm)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
        self.zmq_socket.bind(open_address)
        self._sync(sync_address, config)

    def _sync(self, sync_address, config):
        ctx = zmq.Context.instance()
        s = ctx.socket(zmq.REP)
        s.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
        s.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
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
