"""
Realization of EnoughResourcesChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List
from datetime import timedelta

from src.load_analyzers.triggers import Trigger
from . import Checker


class EnoughResourcesChecker(Checker):
    """
    This checker, checks that enough resources are available
    """

    def make_triggers(self) -> List[Trigger]:
        models = self.input_batch_queue.get_models(is_stateless=True)
        running_models = self.model_instances_storage.get_running_models()
        marked_models = self.model_instances_storage.get_models_with_errors(
            new_chance_delta=timedelta(seconds=30)
        )
        required_models = set(models) - set(running_models) - set(marked_models)
        triggers = map(self.make_increase_trigger, required_models)
        return list(triggers)
