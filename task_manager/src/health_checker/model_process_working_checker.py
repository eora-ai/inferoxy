"""
This module implements concrete health checker that model process is working
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time

import zmq
import zmq.asyncio
from loguru import logger

import src.data_models as dm
from src.cloud_clients import BaseCloudClient

from .checker import BaseHealthChecker, Status


class ModelProcessWorkingChecker(BaseHealthChecker):
    def __init__(self, cloud_client: BaseCloudClient, ports=None, zmq_config=None):
        super().__init__(cloud_client)
        self.ctx = zmq.asyncio.Context()

        if ports is None:
            self.ports = self.read_ports()
        if zmq_config is None:
            self.zmq_config = self.read_zmq_config()

    async def check(self, model_instance: dm.ModelInstance) -> Status:
        try:
            sock = self.__get_sock(model_instance)
        except Exception as e:
            logger.warning("Cannot connect to model_instance")
            return Status(
                model_instance=model_instance,
                is_running=False,
                reason="Can not connect to model_instance, {e}",
            )
        is_running, reason = self.__check_model_instance(sock)
        sock.close()
        return Status(
            model_instance=model_instance, is_running=is_running, reason=reason
        )

    async def __get_sock(self, model: dm.ModelInstance) -> zmq.asyncio.Socket:
        sock = self.ctx.socket(zmq.REQ)
        sock.setsockopt(zmq.SNDTIMEO, self.zmq_config.zmq_sndtimeo)
        sock.setsockopt(zmq.RCVTIMEO, self.zmq_config.zmq_rcvtimeo)
        sock.connect(
            model.host,
        )
        logger.info(f"Make socket for req/rep in {self.__class__.__name__}")
        return sock

    @staticmethod
    async def __get_address(hostname: str, port: int) -> str:
        return ""

    async def __check_model_instance(self, sock: zmq.asyncio.Socket) -> Status:
        sock.send(b"CHECK")
        time.sleep(1)
        result = sock.recv()
        if result == b"OK":
            return (True, None)
        return (False, "Model returns {result}")

    @staticmethod
    def read_ports():
        return {}

    @staticmethod
    def read_config():
        return {}

    @staticmethod
    def read_zmq_config():
        return
