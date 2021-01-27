"""
Connection stable checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time

import src.data_models as dm
from .checker import BaseHealthChecker, Status
from .errors import ConnectionIdleTimeout


class ConnectionChecker(BaseHealthChecker):
    async def check(self, model_instance: dm.ModelInstance) -> Status:
        if not model_instance.lock:
            return Status(model_instance=model_instance, is_running=True, reason=None)

        last_sent_batch = model_instance.sender.get_time_of_last_sent_batch()

        last_received_batch = model_instance.receiver.get_time_of_last_received_batch()

        cur = time.time()
        if cur - last_sent_batch < 10 or cur - last_received_batch < 10:
            return Status(model_instance=model_instance, is_running=True, reason=None)

        return Status(
            model_instance=model_instance,
            is_running=False,
            reason=ConnectionIdleTimeout("Nothing was sent or received in 10 seconds"),
        )
