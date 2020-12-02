"""
Entry point of processing input queue of batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from asyncio import QueueEmpty

from src.batch_queue import InputBatchQueue
from src.batch_processing.adapter_model_instance import AdapterModelInstance
from src.model_instances_storage import ModelInstancesStorage


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
        models = model_instances_storage.get_running_models()
        tasks = []
        for model in models:
            try:
                batch = await input_batch_queue.get_nowait(tag=model)
            except QueueEmpty:
                continue
            model_instance = model_instances_storage.get_next_running_instance(model)
            adapter_model_instance = AdapterModelInstance(model_instance)
            tasks.append(adapter_model_instance.send(batch))
        await asyncio.wait(tasks)
