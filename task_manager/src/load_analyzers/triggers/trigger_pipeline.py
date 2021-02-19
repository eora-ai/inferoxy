"""
Base class for trigger pipeline
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora"

from functools import reduce
from collections import defaultdict
from typing import List, Iterable, Dict, Optional, Type

from loguru import logger

import src.data_models as dm
from src.cloud_clients import BaseCloudClient
from . import Trigger, DecreaseTrigger, IncreaseTrigger
from src.model_instances_storage import ModelInstancesStorage


class TriggerPipeline:
    """
    Data structure to store triggers, and filter them
    """

    def __init__(
        self,
        cloud_client: BaseCloudClient,
        model_instances_storage: ModelInstancesStorage,
        config: dm.Config,
    ):
        self.__triggers: List[Trigger] = []
        self.__cloud_client = cloud_client
        self.__model_instances_storage = model_instances_storage
        self.__max_model_percent = (
            config.load_analyzer.trigger_pipeline.max_model_percent
        )

    def append(self, trigger: Trigger):
        """
        Append trigger to triggers
        """
        self.__triggers.append(trigger)

    def extend(self, triggers: Iterable[Trigger]):
        """
        Extend internal triggers by another iterable of triggers
        """
        self.__triggers.extend(triggers)

    def optimize(self):
        """
        Optimize pipeline. Kind a sort of triggers, and reduces unnecessary triggers
        """

        # Firstly left all stateful decrease triggers
        temp_triggers, self.__triggers = self.__triggers[:], []
        stateful_decrease_triggers = filter(
            lambda x: not x.stateless and isinstance(x, DecreaseTrigger), temp_triggers
        )
        self.__triggers.extend(stateful_decrease_triggers)

        # Left all stateful increase triggers if there is enough space

        stateful_increase_triggers = list(
            filter(
                lambda x: not x.stateless and isinstance(x, IncreaseTrigger),
                temp_triggers,
            )
        )
        conflicts = self.get_conflicted_triggers(
            self.__triggers + stateful_increase_triggers
        )
        #        logger.debug(
        #            f"Conflicts after appending stateful increase triggers {conflicts}"
        #        )
        while stateful_increase_triggers and conflicts:
            stateful_increase_triggers = filter(
                lambda x: x not in conflicts, stateful_increase_triggers
            )
            conflicts = self.get_conflicted_triggers(
                self.__triggers + stateful_increase_triggers
            )

        self.__triggers.extend(stateful_increase_triggers)

        # Left only one stateless decrease triggers

        stateless_decrease_triggers = list(
            filter(
                lambda x: x.stateless and isinstance(x, DecreaseTrigger), temp_triggers
            )
        )
        if stateless_decrease_triggers:
            self.__triggers.extend(stateless_decrease_triggers[:1])

        # Left all stateless increase triggers if there is enough space
        stateless_increase_triggers = list(
            filter(
                lambda x: x.stateless and isinstance(x, IncreaseTrigger),
                temp_triggers,
            )
        )
        conflicts = self.get_conflicted_triggers(
            self.__triggers + stateless_increase_triggers
        )
        # logger.debug(
        #    f"Conflicts after appending stateless increase triggers {conflicts}"
        # )
        while stateless_increase_triggers and conflicts:
            stateless_increase_triggers = list(
                filter(lambda x: x not in conflicts, stateless_increase_triggers)
            )
            conflicts = self.get_conflicted_triggers(
                self.__triggers + stateless_increase_triggers
            )

        self.__triggers.extend(stateless_increase_triggers)

    def get_conflicted_triggers(self, triggers: List[Trigger] = None) -> List[Trigger]:
        """
        Checks that, can pipeline be applied, and returns confliced triggers, that should be removed
        """
        if triggers is None:
            triggers = self.__triggers[:]

        # Get maximum number of instances
        maximum_running_models = self.__cloud_client.get_maximum_running_instances()

        # Get Dict[ModelObject, number of instances] for stateless

        current_running_models = (
            self.__model_instances_storage.get_running_models_with_source_ids()
        )

        current_number_by_models: Dict[
            dm.ModelObject, int
        ] = self.__model_instances_storage.get_number_of_running_instancse()
        # Check that after pipeline appleing there are less than 70% of one model

        conflicted_triggers: List[Trigger] = []

        number_by_models = self.draft_apply(current_number_by_models, triggers, [])

        while sum(number_by_models.values()) > maximum_running_models:
            trigger = self.get_trigger(
                triggers, trigger_type=IncreaseTrigger, model=None
            )
            conflicted_triggers += [] if trigger is None else [trigger]
            number_by_models = self.draft_apply(
                current_number_by_models, triggers, conflicted_triggers
            )

        for model, num in number_by_models.items():
            if num / maximum_running_models * 100 > self.__max_model_percent:
                trigger = self.get_trigger(
                    triggers, trigger_type=IncreaseTrigger, model=model
                )
                conflicted_triggers += [] if trigger is None else [trigger]

        return conflicted_triggers

    def draft_apply(
        self,
        current_number_by_models: Dict[dm.ModelObject, int],
        triggers: Optional[List[Trigger]],
        conflicted_triggers: Optional[List[Trigger]] = None,
    ) -> Dict[dm.ModelObject, int]:
        """
        Draft apply triggers to current state

        Parameters
        ----------
        current_number_by_models:
            Current state, represent number of running models
        """

        if triggers is None:
            triggers = self.__triggers

        if conflicted_triggers is None:
            conflicted_triggers = []

        number_by_models = current_number_by_models.copy()
        for trigger in triggers:
            if trigger in conflicted_triggers:
                continue
            if (
                isinstance(trigger, DecreaseTrigger)
                and trigger.model_instance is not None
            ):
                number_by_models[trigger.model_instance.model] -= 1
            if isinstance(trigger, IncreaseTrigger) and trigger.model is not None:
                number_by_models[trigger.model] += 1
        return number_by_models

    async def apply(self) -> None:
        """
        Apply all triggers, and return all ModelInstances. Triggers must be optimized
        """
        for trigger in self.__triggers:
            trigger.set_cloud_client(self.__cloud_client)
            model_instance = trigger.apply()
            if model_instance is not None and trigger.model_instance != model_instance:
                self.__model_instances_storage.add_model_instance(model_instance)
            elif (
                trigger.model_instance == model_instance and not model_instance is None
            ):
                await self.__model_instances_storage.remove_model_instance(
                    model_instance
                )

    def get_trigger(
        self,
        triggers: Optional[List[Trigger]] = None,
        trigger_type: Type[Trigger] = IncreaseTrigger,
        model: Optional[dm.ModelObject] = None,
    ) -> Optional[Trigger]:
        """
        Search in `triggers` first trigger with type `trigger_type` and for model `model`
        """
        if triggers is None:
            triggers = self.__triggers

        for trigger in triggers:
            trigger_model: Optional[dm.ModelObject]
            if trigger.model is not None:
                trigger_model = trigger.model
            elif trigger.model_instance is not None:
                trigger_model = trigger.model_instance.model
            else:
                trigger_model = None
            if isinstance(trigger, trigger_type) and (
                model is None or model == trigger_model
            ):
                return trigger
        return None

    def get_triggers(self) -> List[Trigger]:
        """
        Getter for `__triggers`
        """
        return self.__triggers

    def __len__(self) -> int:
        return len(self.__triggers)
