"""
Store connections for model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


from datetime import datetime

from loguru import logger

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue


class AdapterV1ModelInstance:
    """
    Make adapter between BatchRequest and model v3 format
    """

    def __init__(
        self,
        model_instance: dm.ModelInstance,
        input_queue: InputBatchQueue,
        output_queue: OutputBatchQueue,
    ):
        logger.debug("Start to create adapter")
        self.model_instance = model_instance
        self.sender = model_instance.sender
        self.input_queue = input_queue
        self.output_queue = output_queue
        logger.debug("Adapter created")

    async def send(self, batch: dm.RequestBatch):
        """
        Parse batches into v3 model request
        """
        if not self.model_instance.running:
            logger.error("{self.model_instance=} does not running")
            if batch.retries < 3:
                batch.status = dm.Status.ERROR
                await self.input_queue.put(batch)
            else:
                logger.critical(
                    "{self.model_instance.model=} have problem with starting up. Send {batch.uid=} to output queue with error"
                )
                response_batch = dm.ResponseBatch.from_minimal_batch_object(
                    batch, error="Retried over than 3 times. ModelInstance not running"
                )
                await self.output_queue.put(response_batch)
        self.model_instance.current_processing_batch = batch
        batch.status = dm.Status.SENT_TO_MODEL
        batch.started_at = datetime.now()
        logger.info("Try to send batch")
        await self.sender.send(batch)
        logger.info("Batch sent")
