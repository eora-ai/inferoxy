"""
This module is responsible for analyze load on task manager, and increase or decrease amount of instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from threading import Thread
import time
from abc import ABC, abstractmethod

from src.cloud_client import BaseCloudClient
from src.batch_queue import InputBatchQueue, OutputBatchQueue


class BaseLoadAnalyzer(Thread, ABC):
    """
    Base class that analyze load, and increases/decreases amount of model instances
    """

    def __init__(
        self,
        cloud_client: BaseCloudClient,
        input_batch_queue: InputBatchQueue,
        output_batch_queue: OutputBatchQueue,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.cloud_client = cloud_client
        self.input_batch_queue = input_batch_queue
        self.output_batch_queue = output_batch_queue


class RunningMeanLoadAnalyzer(BaseLoadAnalyzer):
    """
    Load analyzer based on running mean of request per model
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.means = dict()

    def run(self):
        """
        Entry point of thread
        """
        while True:
            self.check_at_least_one_model_instance()
            time.sleep(0.1)

    def check_at_least_one_model_instance(self):
        models = self.input_batch_queue.tags
        for model in models:
            if len(self.cloud_client.get_running_instances(model)) < 0:
                self.cloud_client.start_instance(model)
