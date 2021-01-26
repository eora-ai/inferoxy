"""
This module is an implementation of BaseChecker, that checks is container running in cloud
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import src.data_models as dm

from .checker import BaseHealthChecker, Status


class ContainerRunningChecker(BaseHealthChecker):
    """
    Checking that container is running in the cloud
    """

    async def check(self, model_instance: dm.ModelInstance) -> Status:
        reasoning_output = self.cloud_client.is_instance_running(model_instance)
        return Status(model_instance, reasoning_output.output, reasoning_output.reason)
