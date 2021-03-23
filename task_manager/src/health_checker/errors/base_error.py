"""
Base classes for health check errors
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

import src.data_models as dm
from src.model_instances_storage import ModelInstancesStorage

if TYPE_CHECKING:
    from src.alert_sender import BaseAlertManager


class HealthCheckError(ABC):
    """
    Base class of errors
    """

    code: Optional[str] = None

    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    async def process(
        self,
        model_instance_storage: ModelInstancesStorage,
        model_instance: dm.ModelInstance,
        alert_manager: "BaseAlertManager",
    ):
        """
        Process error, there are several behaviors.
        First one send error to alert manager,
        second one is to re run task that was running on failure model_instance
        """

    def __str__(self):
        return f"[{self.code}]: {self.description}"

    def __repr__(self):
        return str(self.code)


class FatalError(HealthCheckError):
    """
    Fatal error is occured, like bug in the model. There is no sense in try to restart a task.
    """

    async def process(
        self,
        model_instance_storage: ModelInstancesStorage,
        model_instance: dm.ModelInstance,
        alert_manager: "BaseAlertManager",
    ):
        model_instance.running = False
        await model_instance_storage.remove_model_instance(model_instance)
        model_instance_storage.errors[model_instance.model] += 1
        await alert_manager.send(model_instance, self)


class RetriableError(HealthCheckError):
    """
    We can to retry a task.
    """

    async def process(
        self,
        model_instance_storage: ModelInstancesStorage,
        model_instance: dm.ModelInstance,
        alert_manager: "BaseAlertManager",
    ):
        model_instance.lock = False
        model_instance.current_processing_batch = None
        await alert_manager.retry_task(model_instance, self)
