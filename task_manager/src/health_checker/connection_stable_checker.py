"""
Connection stable checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time

import src.data_models as dm
from .errors import ConnectionIdleTimeout
from .checker import BaseHealthChecker, Status


class ConnectionChecker(BaseHealthChecker):
    def check(self, model_instance: dm.ModelInstance) -> Status:
        if not model_instance.lock:
            return Status(model_instance=model_instance, is_running=True, reason=None)

        if self.config is None:
            raise ValueError("Config can not be none")

        last_sent_batch = model_instance.sender.get_time_of_last_sent_batch()

        last_received_batch = model_instance.receiver.get_time_of_last_received_batch()

        cur = time.time()
        if (
            cur - last_sent_batch < self.config.health_check.connection_idle_timeout
            or cur - last_received_batch
            < self.config.health_check.connection_idle_timeout
        ):
            return Status(model_instance=model_instance, is_running=True, reason=None)

        return Status(
            model_instance=model_instance,
            is_running=False,
            reason=ConnectionIdleTimeout(
                f"Nothing was sent or received in {self.config.health_check.connection_idle_timeout} seconds"
            ),
        )
