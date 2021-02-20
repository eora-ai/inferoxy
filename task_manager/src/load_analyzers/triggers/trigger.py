"""
Base class for increases and decreases triggers.
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora"

from typing import Optional
from abc import ABC, abstractmethod

import src.data_models as dm
from src.cloud_clients import BaseCloudClient


class Trigger(ABC):
    """
    Trigger abstract class, main function is an apply function
    """

    def __init__(
        self,
        model: Optional[dm.ModelObject] = None,
        model_instance: Optional[dm.ModelInstance] = None,
        stateless: bool = True,
    ):
        self.cloud_client: Optional[BaseCloudClient] = None
        self.model = model
        self.model_instance = model_instance
        self.stateless = stateless

    def set_cloud_client(self, cloud_client: BaseCloudClient) -> None:
        """
        Set concrete cloud client

        Parameters
        ----------
        cloud_client:
            Concrete cloud client
        """
        self.cloud_client = cloud_client

    @abstractmethod
    async def apply(self) -> Optional[dm.ModelInstance]:
        """
        Apply trigger to cloud client
        """

    def __repr__(self):
        return f"{str(type(self))} - {self.model=} - {self.model_instance=}"
