"""
Entry point of processing input queue of batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from asyncio import QueueEmpty
from typing import List, Tuple, Optional

from loguru import logger

from src.batch_queue import InputBatchQueue
from src.batch_processing.adapter_model_instance import AdapterV1ModelInstance
from src.model_instances_storage import ModelInstancesStorage
from src.exceptions import TagDoesNotExists
import src.data_models as dm


async def send_to_model(
    input_batch_queue: InputBatchQueue,
    model_instances_storage: ModelInstancesStorage,
):
    """
    Get batch from input_batch_queue and send it to existing model_instance

    Parameters
    ----------
    input_batch_queue:
        Input batch queue, taged queue with batches
    """
    while True:
        models_by_sources_ids: List[
            Tuple[Optional[str], dm.ModelObject]
        ] = model_instances_storage.get_running_models_with_source_ids()
        tasks = []
        for (source_id, model) in models_by_sources_ids:
            try:
                if not model.stateless:
                    batch = await input_batch_queue.get_nowait(
                        model=model, source_id=source_id
                    )
                else:
                    batch = await input_batch_queue.get_nowait(model=model)
            except (QueueEmpty, TagDoesNotExists):
                continue
            model_instance = model_instances_storage.get_next_running_instance(
                model, source_id
            )
            if model_instance is None:
                logger.warning(
                    f"Model Instance Storage return None, for {model=} and {source_id=}"
                )
                continue
            adapter_model_instance = AdapterV1ModelInstance(model_instance)
            tasks.append(adapter_model_instance.send(batch))
        await asyncio.wait(tasks)
