"""
This module is responsible for manage cloud.
Increase, decrease and get operations over model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Optional
from abc import ABC, abstractmethod

import src.data_models as dm
from src.health_checker.errors import HealthCheckError


class BaseCloudClient(ABC):
    """
    Operation over cloud, Base class needed because want different cloud
    client, for k8s and for docker-compose/docker
    """

    def __init__(self, config: Optional[dm.Config]):
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
            Information of the model instance, name of
            the pod/container and address
        """

    @abstractmethod
    def get_maximum_running_instances(self) -> int:
        """
        Return maximum number of running instances
        """

    @abstractmethod
    def is_instance_running(
        self, model_instance: dm.ModelInstance
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        """
        Returns true if instance is running, else returns false, and description why

        Parameters
        ----------
        model_instance:
            The Model instance that we want to check
        """
