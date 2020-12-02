"""
This module is responsible for manage cloud.
Increase, decrease and get operations over model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from abc import ABC, abstractmethod
from typing import List

import src.data_models as dm
from src.utils.data_transfers import Receiver, Sender


class BaseCloudClient(ABC):
    """
    Operation over cloud, Base class needed because want different cloud client, for k8s and for docker-compose/docker
    """

    def __init__(self, config: dm.Config):
        self.config = config

    @abstractmethod
    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        """
        Get all running model instances by model

        Parameters
        ----------
        model:
            Model object, need to get name of the model
        """

    @abstractmethod
    def can_create_instance(self, model: dm.ModelObject) -> bool:
        """
        Check, if there are a space/instances for new model instances

        Parameters
        ----------
        model:
            Model object, need to get name of the model
        """

    @abstractmethod
    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        """
        Start a model instance

        Parameters
        ----------
        model:
            Model object
        """

    @abstractmethod
    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop a model instance
        Parameters
        ----------
        model_instance:
            Information of the model instance, name of the pod/container and address
        """


class DockerCloudClient(BaseCloudClient):
    """
    Implementation of docker based cloud
    """

    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        return []

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        return True

    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        return dm.ModelInstance(model=model, sender=Sender(), receiver=Receiver())

    def stop_instance(self, model_instance: dm.ModelInstance):
        pass
