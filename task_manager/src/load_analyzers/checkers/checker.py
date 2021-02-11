"""
Base checker class
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Optional
from abc import ABC, abstractmethod

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage
from src.load_analyzers.triggers import Trigger, IncreaseTrigger, DecreaseTrigger


class Checker(ABC):
    """
    Base class of checker, that analyze load and make triggers
    """

    def __init__(
        self,
        model_instances_storage: ModelInstancesStorage,
        input_batch_queue: InputBatchQueue,
        output_batch_queue: OutputBatchQueue,
        config: Optional[dm.Config] = None,
    ):
        self.model_instances_storage = model_instances_storage
        self.input_batch_queue = input_batch_queue
        self.output_batch_queue = output_batch_queue
        self.config = config

    def __call__(self) -> List[Trigger]:
        return self.make_triggers()

    @abstractmethod
    def make_triggers(self) -> List[Trigger]:
        """
        Main method that make triggers out of analyse of input queue and output queue
        """

    @staticmethod
    def make_incerease_trigger(model: dm.ModelObject) -> IncreaseTrigger:
        """
        Make increase trigger out of ModelObject

        Parameters
        ----------
        model:
            Model object which will be used to make IncreaseTrigger
        """
        return IncreaseTrigger(model=model)

    @staticmethod
    def make_decrease_trigger(model_instance: dm.ModelInstance) -> DecreaseTrigger:
        """
        Make decrease trigger out of ModelInstance
        """
        return DecreaseTrigger(model_instance=model_instance)
