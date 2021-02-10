"""
Concrete checker, that analyze running mean of load
make Increase trigger if load > max threshold,
and make Decrease Trigger if load < min threshold
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import collections
from typing import Dict, List, Deque

import src.data_models as dm
from .checker import Checker
from src.load_analyzers.triggers import Trigger


class RunningMeanStatelessChecker(Checker):
    """
    Analyze time of processing needed on each batch,
    and make prediction how much time needed to process remaining batches.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.config is None:
            raise ValueError("Config parameter must be set")
        self.min_threshold = self.config.load_analyzer.running_mean.min_threshold
        self.max_threshold = self.config.load_analyzer.running_mean.max_threshold
        self.window_size = self.config.load_analyzer.running_mean.window_size
        self.processing_times: Dict[dm.ModelObject, Deque[float]] = {}
        self.means: Dict[dm.ModelObject, float] = {}

    def calculate_means(self):
        """
        Calculate maens by model
        """
        batches_time_processing = self.output_batch_queue.batches_time_processing.copy()
        self.output_batch_queue.batches_time_processing.clear()
        for response_batch in batches_time_processing:
            processing_time = batches_time_processing[response_batch]["processing_time"]
            count = batches_time_processing[response_batch]["count"]
            if response_batch.model not in self.processing_times:
                self.processing_times[response_batch.model] = collections.deque(
                    maxlen=self.window_size
                )
            self.processing_times[response_batch.model].append(processing_time / count)

        self.means.clear()
        for model in self.processing_times:
            self.means[model] = sum(self.processing_times[model]) / len(
                self.processing_times[model]
            )

    def estimate_processing_time(
        self, model: dm.ModelObject, average_processing_time: float
    ) -> float:
        """
        Calculate how long it takes to process input_queue for model
        """
        requests_in_queue = self.input_batch_queue.get_num_requests_in_queue(model)
        if len(self.model_instances_storage.get_model_instances(model)) == 0:
            return self.max_threshold + 1
        return (
            requests_in_queue
            * average_processing_time
            / len(self.model_instances_storage.get_model_instances(model))
        )

    def make_triggers(self) -> List[Trigger]:
        self.calculate_means()
        triggers: List[Trigger] = []
        for model, average_processing_time in self.means.items():
            estimated_time = self.estimate_processing_time(
                model, average_processing_time
            )
            if estimated_time > self.max_threshold:
                triggers += [self.make_incerease_trigger(model)]
            elif (
                estimated_time < self.min_threshold
                and len(self.model_instances_storage.get_model_instances(model)) > 1
            ):
                model_instance = (
                    self.model_instances_storage.get_not_locked_model_instances(
                        model=model
                    )
                )[0]
                model_instance.lock = True
                triggers += [self.make_decrease_trigger(model_instance=model_instance)]
            elif estimated_time == 0:
                model_instance = (
                    self.model_instances_storage.get_not_locked_model_instances(
                        model=model
                    )
                )[0]
                model_instance.lock = True
                triggers += [self.make_decrease_trigger(model_instance=model_instance)]
            else:
                continue
        return triggers
