import zmq  # type: ignore

context = zmq.Context()


class Sender:
    """Opens zmq PUSH socket and sends python obj."""

    def __init__(self, open_address, config):

        self.zmq_context = context
        self.zmq_socket = self.zmq_context.socket(zmq.PUSH)
        self.zmq_socket.setsockopt(zmq.SNDHWM, config.zmq_sndhwm)
        self.zmq_socket.setsockopt(zmq.SNDTIMEO, config.zmq_sndtimeo)
        self.zmq_socket.bind(open_address)

    def send(self, data):
        self.zmq_socket.send_pyobj(data)

    def close(self):
        self.zmq_socket.close()


class Receiver:
    """Opens zmq PULL socket and receives python obj."""

    def __init__(self, open_address, config):

        self.zmq_context = context
        self.zmq_socket = self.zmq_context.socket(zmq.PULL)
        self.zmq_socket.setsockopt(zmq.RCVHWM, config.zmq_rcvhwm)
        self.zmq_socket.setsockopt(zmq.RCVTIMEO, config.zmq_rcvtimeo)
        self.zmq_socket.bind(open_address)

    def receive(self):
        data = self.zmq_socket.recv_pyobj()
        return data

    def close(self):
        self.zmq_socket.close()
