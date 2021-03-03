"""
This module is an implementation of BaseChecker, that checks is container running in cloud
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from loguru import logger

import src.data_models as dm
from .checker import BaseHealthChecker, Status
from .errors import ContainerDoesNotExists, ContainerExited


class ContainerRunningChecker(BaseHealthChecker):
    """
    Checking that container is running in the cloud
    """

    def check(self, model_instance: dm.ModelInstance) -> Status:
        reasoning_output = self.cloud_client.is_instance_running(model_instance)
        status = Status(
            model_instance, reasoning_output.output, reason=reasoning_output.reason
        )
        return status
