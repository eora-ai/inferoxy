"""
This module is responsible for analyze load on task manager,
and increase or decrease amount of instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from abc import ABC
from typing import List, Type

from loguru import logger

import src.data_models as dm
from src.cloud_clients import BaseCloudClient
from src.load_analyzers.checkers import Checker
from src.load_analyzers.triggers import TriggerPipeline
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.model_instances_storage import ModelInstancesStorage


class BaseLoadAnalyzer(ABC):
    """
    Base class that analyze load, and increases/decreases amount of model instances
    """

    def __init__(
        self,
        cloud_client: BaseCloudClient,
        input_batch_queue: InputBatchQueue,
        output_batch_queue: OutputBatchQueue,
        model_instances_storage: ModelInstancesStorage,
        config: dm.Config,
    ):
        logger.info("Start load analyzer")
        self.sleep_time = config.load_analyzer.sleep_time
        self.cloud_client = cloud_client
        self.input_batch_queue = input_batch_queue
        self.output_batch_queue = output_batch_queue
        self.model_instances_storage = model_instances_storage
        self.config = config
        for checker_class in self.checkers:
            self.__checkers.append(
                checker_class(
                    self.model_instances_storage,
                    self.input_batch_queue,
                    self.output_batch_queue,
                    self.config,
                )
            )

    checkers: List[Type[Checker]] = []
    __checkers: List[Checker] = []

    async def analyzer_pipeline(self):
        """
        Make triggers and apply them
        """
        while True:
            await asyncio.sleep(self.sleep_time)
            logger.debug("Load analyzer tick")
            pipeline = TriggerPipeline(
                cloud_client=self.cloud_client,
                model_instances_storage=self.model_instances_storage,
                config=self.config,
            )
            for checker in self.__checkers:
                triggers = checker.make_triggers()
                pipeline.extend(triggers)
            pipeline.optimize()
            if len(pipeline) != 0:
                logger.info(f"Pipeline that will be applied {pipeline.get_triggers()}")
            await pipeline.apply()
