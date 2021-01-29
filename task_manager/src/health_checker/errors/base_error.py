"""
Base classes for health check errors
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from abc import ABC, abstractmethod
from typing import Optional


class HealthCheckError(ABC):
    """
    Base class of errors
    """

    code: Optional[str] = None

    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def process(self, alert_manager):
        """
        Process error, there are several behaviors.
        First one send error to alert manager,
        second one is to re run task that was running on failure model_instance
        """

    def __repr__(self):
        return f"[{self.code}]: {self.description}"


class FatalError(HealthCheckError):
    """
    Fatal error is occured, like bug in the model. There is no sense in try to restart a task.
    """

    def process(self, alert_manager):
        alert_manager.send(repr(self))


class RetriableError(HealthCheckError):
    """
    We can to retry a task.
    """

    def process(self, alert_manager):
        pass  # TODO: retry a task
