"""
Realization of EnoughResourcesChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List

from src.load_analyzers.triggers import Trigger
from . import Checker


class EnoughResourcesChecker(Checker):
    """
    This checker, checks that enough resources are available
    """

    def make_triggers(self) -> List[Trigger]:
        models = self.input_batch_queue.get_models(is_stateless=True)
        running_models = self.model_instances_storage.get_running_models()
        required_models = set(models) - set(running_models)
        triggers = map(self.make_incerease_trigger, required_models)
        return list(triggers)
