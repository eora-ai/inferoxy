"""
ZeroMQ adapter that receive python objects based on BaseAdapter
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from loguru import logger
import zmq  # type: ignore # type: ignore

import src.data_models as dm

from .base_adapter import BaseAdapter, Request, Response


class ZMQPythonAdapter(BaseAdapter):
    """
    Adapter that listen on zmq socket, and receives python objects(dict)
    """

    def init_server(self, config: dm.Config):
        self.input_zmq_socket = self.ctx.socket(zmq.PULL)
        self.input_zmq_socket.bind(config.zmq_python.listen_address)
        self.output_zmq_socket = self.ctx.socket(zmq.PUB)
        self.output_zmq_socket.bind(config.zmq_python.send_address)

    def receive_request(self) -> Request:
        try:
            return self.input_zmq_socket.recv_pyobj(zmq.NOBLOCK)
        except zmq.error.Again as exc:
            raise TimeoutError() from exc

    def input_to_request_object(self, req: Request) -> dm.RequestObject:
        if not isinstance(req, dict):
            raise ValueError("Input must be dict")

        try:
            source_id = f"zmq_python:{req['source_id']}"
            request_info = dm.RequestInfo(req["input"], req["parameters"])
            model = self._get_model_object(req["model"])
            return dm.RequestObject(
                self._generate_uid(),
                source_id=source_id,
                request_info=request_info,
                model=model,
            )
        except KeyError as exc:
            raise ValueError("Incorrect forma of the dict") from exc

    def send_result(self, response: Response):
        if not isinstance(response, dict):
            raise ValueError("Response must be a dict")
        self.output_zmq_socket.send_string(response["source_id"], zmq.SNDMORE)
        self.output_zmq_socket.send_pyobj(response)

    def to_response(self, response: dm.ResponseObject) -> Response:
        resp = response.to_dict()
        resp["source_id"] = response.source_id.split(":")[1]
        return resp
