"""
Connection stable checker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import src.data_models as dm
from .checker import BaseHealthChecker, Status


class ConnectionChecker(BaseHealthChecker):
    def check(self, model_instance: dm.ModelInstance) -> Status:
        return Status(model_instance=model, is_running=True, reason=None)
