"""
Realization of StatefulChecker
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time
from typing import List
from datetime import timedelta

from loguru import logger

from src.load_analyzers.triggers import Trigger
import src.data_models as dm
from . import Checker


class StatefulChecker(Checker):
    """
    This checker checks that enough resources are available
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.config is None:
            raise ValueError("Config parameter must be set")
        self.config: dm.Config = self.config

    def make_triggers(self) -> List[Trigger]:
        requested_models_with_sources = (
            self.input_batch_queue.get_models_with_source_ids(is_stateless=False)
        )
        running_models_with_sources = (
            self.model_instances_storage.get_running_models_with_source_ids(
                is_stateless=False
            )
        )

        marked_models = self.model_instances_storage.get_models_with_errors(
            new_chance_delta=timedelta(seconds=30)
        )
        triggers: List[Trigger] = []

        logger.debug(f"Request models with sources ids {requested_models_with_sources}")
        logger.debug(f"Running models with sources {running_models_with_sources}")

        for source_id, model in requested_models_with_sources:
            logger.debug(
                f"Search for {(source_id, model)} in {running_models_with_sources}"
            )
            if (source_id, model) in running_models_with_sources:
                continue

            if (None, model) in running_models_with_sources:
                i = running_models_with_sources.index((None, model))
                running_models_with_sources[i] = (source_id, model)
                logger.debug(f"Try to set {source_id=} for {model=}")
                if not source_id is None:
                    self.model_instances_storage.set_source_id(model, source_id)
                continue
            if model in marked_models:
                continue

            triggers += [self.make_increase_trigger(model)]

        logger.debug(f"Left {running_models_with_sources=}")
        for (source_id, model) in running_models_with_sources:
            model_instance = self.model_instances_storage.get_model_instance(
                model=model, source_id=source_id
            )
            if model_instance is None:
                continue
            if (
                time.time() - model_instance.sender.get_time_of_last_sent_batch()
                > self.config.load_analyzer.stateful_checker.keep_model
            ):
                triggers += [self.make_decrease_trigger(model_instance=model_instance)]

        return triggers
