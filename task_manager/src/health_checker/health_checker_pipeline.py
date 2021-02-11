"""
Aggregate checkers
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import List
from threading import Thread

from loguru import logger

import src.data_models as dm
from src.cloud_clients import BaseCloudClient
from src.alert_sender import BaseAlertManager
from .checker import BaseHealthChecker, Status
from .connection_stable_checker import ConnectionChecker
from src.model_instances_storage import ModelInstancesStorage
from .container_running_checker import ContainerRunningChecker


class HealthCheckerPipeline(Thread):
    def __init__(
        self,
        model_instances_storage: ModelInstancesStorage,
        cloud_client: BaseCloudClient,
        alert_manager: BaseAlertManager,
        config: dm.Config,
    ):
        super().__init__()
        self.model_instances_storage = model_instances_storage
        self.config = config
        self.checkers: List[BaseHealthChecker] = [
            ContainerRunningChecker(cloud_client, config),
            ConnectionChecker(cloud_client, config),
        ]
        self.alert_manager = alert_manager

    def run(self):
        asyncio.run(self.pipeline())

    async def pipeline(self):
        while True:
            for (
                model_instance
            ) in self.model_instances_storage.get_all_model_instances():
                error_statuses = []
                for checker in self.checkers:
                    status = await checker.check(model_instance)
                    if not status.is_running:
                        error_statuses.append(status)
                self.make_decision(error_statuses)

            await asyncio.sleep(self.config.load_analyzer.sleep_time)

    async def make_decision(self, statuses: List[Status]):
        """
        Make decision about errors: restart task or send to alert manager
        """
        for status in statuses:
            if status.is_running:
                continue
            if status.reason is None:
                logger.warning("Status reason can not be None")
                continue

            status.reason.process(status.model_instance, self.alert_manager)
            self.model_instances_storage.remove_model_instance(status.model_instance)
