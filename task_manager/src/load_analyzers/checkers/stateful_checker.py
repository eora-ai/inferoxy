"""
Realization of StatefulChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List

from src.load_analyzers.triggers import Trigger

from . import Checker


class StatefulChecker(Checker):
    """
    This checker checks that enough resources are available
    """

    def make_triggers(self) -> List[Trigger]:
        requested_models_with_sources = (
            self.input_batch_queue.get_models_with_source_ids(is_stateless=False)
        )
        running_models_with_sources = (
            self.model_instances_storage.get_running_models_with_source_ids(
                is_stateless=False
            )
        )

        triggers: List[Trigger] = []

        for source_id, model in requested_models_with_sources:
            if (source_id, model) in running_models_with_sources:
                continue

            if (None, model) in running_models_with_sources:
                i = running_models_with_sources.index((None, model))
                running_models_with_sources[i] = (source_id, model)
                continue

            triggers += [self.make_incerease_trigger(model)]

        for (source_id, model) in running_models_with_sources:
            if source_id is None:
                model_instance = self.model_instances_storage.get_model_instance(
                    model=model, source_id=source_id
                )
                if model_instance is None:
                    continue
                triggers += [self.make_decrease_trigger(model_instance=model_instance)]

        return triggers
