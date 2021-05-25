"""
Concreter AlertManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from datetime import datetime

from loguru import logger

import src.data_models as dm
from src.health_checker.errors import HealthCheckError
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from .base_alert_manager import BaseAlertManager


class AlertManager(BaseAlertManager):
    def __init__(self, input_queue: InputBatchQueue, output_queue: OutputBatchQueue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    async def send(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        batch = model_instance.current_processing_batch
        model_instance.current_processing_batch = None
        if batch is None:
            logger.warning(f"{model_instance=} has error {repr(error)}, without task")
            return
        logger.warning(
            f"{model_instance=} has error {repr(error)}, send {batch.uid=} to output"
        )
        batch.status = dm.Status.FAILED
        batch.done_at = datetime.now()
        response_batch = dm.ResponseBatch.from_minimal_batch_object(
            batch, error=str(error)
        )
        await self.__send_to_output_queue(response_batch)

    async def __send_to_output_queue(self, batch: dm.ResponseBatch):
        await self.output_queue.put(batch)

    async def __send_to_input_queue(self, batch: dm.MinimalBatchObject):
        await self.input_queue.put(batch)

    async def retry_task(
        self, model_instance: dm.ModelInstance, error: HealthCheckError
    ):
        logger.warning(f"{model_instance=} has error {repr(error)} retry task")
        batch = model_instance.current_processing_batch
        if batch is None:
            return
        batch.status = dm.Status.ERROR
        await self.__send_to_input_queue(batch)
