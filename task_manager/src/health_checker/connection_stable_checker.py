"""
Connection stable checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import src.data_models as dm
from .checker import BaseHealthChecker, Status


class ConnectionChecker(BaseHealthChecker):
    async def check(self, model_instance: dm.ModelInstance) -> Status:
        if not model_instance.lock:
            return Status(model_instance=model_instance, is_running=True, reason=None)

        return Status(model_instance=model_instance, is_running=True, reason=None)
