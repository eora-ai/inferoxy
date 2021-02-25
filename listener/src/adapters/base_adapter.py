"""
Base Adapter
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


from typing import TypeVar
from uuid import uuid4
from abc import ABC, abstractmethod
from multiprocessing import Process

import zmq  # type: ignore
from loguru import logger

import src.data_models as dm


Request = TypeVar("Request")
Response = TypeVar("Response")


class BaseAdapter(ABC):
    """
    Base Adapter is an abstract class, that provide interface for another adapters
    """

    def __init__(self, config: dm.Config):
        self.config = config
        self.ctx = zmq.Context()
        self.batch_manager_channel = self.__make_batch_manager_channel(config)
        self.debatch_manager_channel = self.__make_debatch_manager_channel(config)

        self.init_server(config)

    def __make_batch_manager_channel(self, config: dm.Config):
        socket = self.ctx.socket(zmq.PUSH)
        socket.connect(config.batch_manager_input_address)
        return socket

    def __make_debatch_manager_channel(self, config: dm.Config):
        socket = self.ctx.socket(zmq.PULL)
        socket.connect(config.debatch_manager_output_address)
        return socket

    @abstractmethod
    def init_server(self, config: dm.Config):
        pass

    @abstractmethod
    def receive_request(self) -> Request:
        pass

    @abstractmethod
    def input_to_request_object(self, req: Request) -> dm.RequestObject:
        pass

    @abstractmethod
    def send_result(self, response: dm.ResponseObject):
        pass

    @abstractmethod
    def to_response(self, response: dm.ResponseObject) -> Response:
        pass

    @staticmethod
    def _generate_uid() -> str:
        # TODO: GET and Increase counter
        # TODO: Make uid from counter
        # TODO: current is not safe
        return str(uuid4())

    def _get_model_object(self, slug: str) -> dm.ModelObject:
        sock = self.ctx.socket(zmq.REQ)
        sock.connect(self.config.model_storage_address)
        sock.send_string(slug)
        model_object = sock.recv_pyobj()
        sock.close()
        del sock
        return model_object

    def _send_request_object(self, req: dm.RequestObject):
        self.batch_manager_channel.send_pyobj(req)

    def _receive_result(self) -> dm.ResponseObject:
        return self.debatch_manager_channel.recv_pyobj(zmq.NOBLOCK)

    @staticmethod
    def _decide_state(request_object: dm.RequestObject):
        request_object.model.stateless = request_object.request_info.parameters.get(
            "stateless", False
        )

    def start(self):
        """
        Start adapter
        """
        logger.info("Starting adapter")
        while True:
            try:
                req = self.receive_request()
                logger.info("Something received. Ура!!!!!")
                req_object = self.input_to_request_object(req)
                self._decide_state(req_object)
                logger.info(f"Request souce_id: {req_object.source_id}")
                self._send_request_object(req_object)
                logger.debug("Req object sent to batch_manager")
            except TimeoutError:
                pass
            except ValueError as exc:
                logger.warning(f"Value error {exc} on request {req}")
            while True:
                try:
                    result = self._receive_result()
                except zmq.error.Again:
                    break
                self.send_result(self.to_response(result))
