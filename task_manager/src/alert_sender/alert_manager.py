"""
Concreter AlertManager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from loguru import logger
from datetime import datetime

import src.data_models as dm
from .base_alert_manager import BaseAlertManager
from src.health_checker.errors import HealthCheckError
from src.batch_queue import InputBatchQueue, OutputBatchQueue


class AlertManager(BaseAlertManager):
    def __init__(self, input_queue: InputBatchQueue, output_queue: OutputBatchQueue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    def send(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        logger.warning(f"{model_instance=} has error {repr(error)}")
        batch = model_instance.current_processing_batch
        if batch is None:
            return
        batch.status = dm.Status.FAILED
        batch.done_at = datetime.now()
        response_batch = dm.ResponseBatch.from_minimal_batch_object(
            batch, error=str(error)
        )
        self.__send_to_output_queue(response_batch)

    def __send_to_output_queue(self, batch: dm.ResponseBatch):
        self.output_queue.put_nowait(batch)

    def __send_to_input_queue(self, batch: dm.MinimalBatchObject):
        self.input_queue.put_nowait(batch)

    def retry_task(self, model_instance: dm.ModelInstance, error: HealthCheckError):
        logger.warning(f"{model_instance=} has error {repr(error)}")
        batch = model_instance.current_processing_batch
        if batch is None:
            return
        batch.status = dm.Status.ERROR
        self.__send_to_input_queue(batch)
