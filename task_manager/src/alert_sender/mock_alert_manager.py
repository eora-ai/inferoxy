"""
Mock alert manager for tests
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Dict

import src.data_models as dm
from src.health_checker.errors import HealthCheckError

from .base_alert_manager import BaseAlertManager


class MockAlertManager(BaseAlertManager):
    """
    MockAlertManager needed for tests, saves errors in `self.errors` field.
    Getter for `self.errors` is `get_errors`
    """

    def __init__(self):
        self.errors: Dict[dm.ModelInstance, HealthCheckError] = {}

    def send(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        self.errors[model_instance] = error

    def retry_task(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        pass

    def get_errors(self) -> Dict[dm.ModelInstance, HealthCheckError]:
        """
        Getter for `self.errors`
        """
        return self.errors
