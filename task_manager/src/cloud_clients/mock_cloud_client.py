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


class MockCloudClient(BaseCloudClient):
    """
    Stub implementation of BaseCloudClient, needed for tests
    """

    def __init__(self, maximum_running_instances=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maximum_running_instances = maximum_running_instances
        self.model_instances: List[dm.ModelInstance] = []

    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        return []

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        return True

    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        model_instance = dm.ModelInstance(
            model=model,
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
    ) -> dm.ReasoningOutput[bool]:
        is_running = model_instance.running
        if not is_running:
            return dm.ReasoningOutput(
                is_running, reason="ModelInstance.running == False"
            )
        is_running &= model_instance in self.model_instances
        if not is_running:
            return dm.ReasoningOutput(
                is_running, reason="ModelInstance created without MockCloudClient"
            )
        return dm.ReasoningOutput(is_running)
