"""
Base classes for health check errors
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Optional
from abc import ABC, abstractmethod


class HealthCheckError(ABC):
    """
    Base class of errors
    """

    code: Optional[str] = None

    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    async def process(self, model_instance, alert_manager):
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

    async def process(self, model_instance, alert_manager):
        await alert_manager.send(model_instance, self)


class RetriableError(HealthCheckError):
    """
    We can to retry a task.
    """

    async def process(self, model_instance, alert_manager):
        await alert_manager.retry_task(model_instance, self)
