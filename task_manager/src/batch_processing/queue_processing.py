"""
Entry point of processing input queue of batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from asyncio import QueueEmpty
from typing import List, Tuple, Optional

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
            Tuple[dm.ModelObject, Optional[str]]
        ] = model_instances_storage.get_running_models_with_source_ids()
        tasks = []
        for (model, source_id) in models_by_sources_ids:
            try:
                if not model.stateless:
                    batch = await input_batch_queue.get_nowait(
                        tag=model, is_stateless=model.stateless, source_id=source_id
                    )
                else:
                    batch = await input_batch_queue.get_nowait(
                        tag=model, is_stateless=model.stateless
                    )
            except (QueueEmpty, TagDoesNotExists):
                continue
            model_instance = model_instances_storage.get_next_running_instance(
                model, source_id
            )
            adapter_model_instance = AdapterV1ModelInstance(model_instance)
            tasks.append(adapter_model_instance.send(batch))
        await asyncio.wait(tasks)
