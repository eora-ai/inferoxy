"""
Alert Manager class
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from abc import ABC, abstractmethod

import src.data_models as dm
from src.health_checker.errors import HealthCheckError


class BaseAlertManager(ABC):
    """
    Interface
    """

    @abstractmethod
    def send(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        """
        Send error into error channel
        """

    @abstractmethod
    def retry_task(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        """
        Retry to process the batch
        """
