"""
This module is responsible for docker based cloud(Actualy it is single machine)
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List

import src.data_models as dm
from src.utils.data_transfers.receiver import BaseReceiver
from src.utils.data_transfers.sender import BaseSender
from src.cloud_clients import BaseCloudClient
from src.health_checker.errors import (
    HealthCheckError,
    ContainerExited,
    ContainerDoesNotExists,
)


class MockCloudClient(BaseCloudClient):
    """
    Stub implementation of BaseCloudClient, needed for tests
    """

    def __init__(self, maximum_running_instances=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maximum_running_instances = maximum_running_instances
        self.model_instances: List[dm.ModelInstance] = []

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        return True

    async def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        model_instance = dm.ModelInstance(
            model=model,
            name=model.name + "_model_instance",
            sender=BaseSender(),
            receiver=BaseReceiver(),
            source_id=None,
            lock=False,
            running=True,
            hostname="Test",
        )
        self.model_instances += [model_instance]
        return model_instance

    def stop_instance(self, model_instance: dm.ModelInstance):
        model_instance.running = False

    def get_maximum_running_instances(self):
        return self.maximum_running_instances

    def is_instance_running(
        self, model_instance: dm.ModelInstance
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        is_running = model_instance.running
        if not is_running:
            return dm.ReasoningOutput(
                is_running, reason=ContainerExited("ModelInstance.running == False")
            )
        is_running &= model_instance in self.model_instances
        if not is_running:
            return dm.ReasoningOutput(
                is_running,
                reason=ContainerDoesNotExists(
                    "ModelInstance created without MockCloudClient"
                ),
            )
        return dm.ReasoningOutput(is_running)
