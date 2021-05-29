"""
Store connections for model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


from datetime import datetime

from loguru import logger

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue


async def adapter_send_to_model(
    batch: dm.RequestBatch,
    model_instance: dm.ModelInstance,
    input_queue: InputBatchQueue,
    output_queue: OutputBatchQueue,
):
    """
    Parse batches into v3 model request
    """
    if not model_instance.running:
        logger.error("{model_instance=} does not running")
        if batch.retries < 3:
            batch.status = dm.Status.ERROR
            await input_queue.put(batch)
        else:
            logger.critical(
                "{model_instance.model=} have problem with starting up. Send {batch.uid=} to output queue with error"
            )
            response_batch = dm.ResponseBatch.from_minimal_batch_object(
                batch, error="Retried over than 3 times. ModelInstance not running"
            )
            await output_queue.put(response_batch)
    model_instance.current_processing_batch = batch
    batch.status = dm.Status.SENT_TO_MODEL
    batch.started_at = datetime.now()
    logger.info("Try to send batch")
    await model_instance.sender.send(batch)
    del batch
    logger.info("Batch sent")
