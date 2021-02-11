"""
This module is definning BaseChecker class
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

import src.data_models as dm
from .errors import HealthCheckError
from src.cloud_clients import BaseCloudClient


@dataclass
class Status:
    """
    Status of model

    Parameters
    ----------
    model_instance:
        ModelInstance object
    is_running:
        Define model is running or not
    reason:
        If model instance is working, than None. If not, reason why model is not working
    """

    model_instance: dm.ModelInstance
    is_running: bool
    reason: Optional[HealthCheckError] = None


class BaseHealthChecker(ABC):
    """
    Abstract class for HealthChecker
    """

    def __init__(
        self, cloud_client: BaseCloudClient, config: Optional[dm.Config] = None
    ):
        self.cloud_client = cloud_client
        self.config = config

    @abstractmethod
    async def check(self, model_instance: dm.ModelInstance) -> Status:
        """
        Check that model is not working
        """
