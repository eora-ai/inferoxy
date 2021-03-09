"""
Aggregate checkers
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import List
import concurrent.futures
from functools import partial

from loguru import logger

import src.data_models as dm
from src.cloud_clients import BaseCloudClient
from src.alert_sender import BaseAlertManager
from src.model_instances_storage import ModelInstancesStorage
from .checker import BaseHealthChecker, Status
from .connection_stable_checker import ConnectionChecker
from .container_running_checker import ContainerRunningChecker


class HealthCheckerPipeline:
    def __init__(
        self,
        model_instances_storage: ModelInstancesStorage,
        cloud_client: BaseCloudClient,
        alert_manager: BaseAlertManager,
        config: dm.Config,
    ):
        super().__init__()
        logger.info("Start heath checkr pipeline")
        self.model_instances_storage = model_instances_storage
        self.config = config
        self.checkers: List[BaseHealthChecker] = [
            ConnectionChecker(cloud_client, config),
            ContainerRunningChecker(cloud_client, config),
        ]
        self.alert_manager = alert_manager

    async def pipeline(self):
        """
        Entry point of health checker pipeline
        """
        loop = asyncio.get_event_loop()
        while True:
            logger.debug("Health checker tick")
            error_statuses = []
            tasks = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                for (
                    model_instance
                ) in self.model_instances_storage.get_all_model_instances():
                    for checker in self.checkers:
                        tasks.append(
                            loop.run_in_executor(
                                executor,
                                partial(checker.check, model_instance),
                            )
                        )
                if tasks:
                    done, _ = await asyncio.wait(tasks)
                    logger.debug(f"Health checker results {done}")
                    error_statuses = [
                        d.result()
                        for d in done
                        if not d.result is None and not d.result().is_running
                    ]

                    logger.debug(f"Statuses {error_statuses}")

            await self.make_decision(error_statuses)
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
            await status.reason.process(
                self.model_instances_storage, status.model_instance, self.alert_manager
            )
