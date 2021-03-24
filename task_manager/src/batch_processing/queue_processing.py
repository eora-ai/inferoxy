"""
Entry point of processing input queue of batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from asyncio import QueueEmpty
from typing import List, Tuple, Optional

from loguru import logger

import src.data_models as dm
from src.batch_queue import InputBatchQueue, OutputBatchQueue
from src.exceptions import TagDoesNotExists
from src.model_instances_storage import ModelInstancesStorage
from src.batch_processing.adapter_model_instance import AdapterV1ModelInstance
from src.health_checker.errors import ContainerExited


async def send_to_model(
    input_batch_queue: InputBatchQueue,
    output_batch_queue: OutputBatchQueue,
    model_instances_storage: ModelInstancesStorage,
):
    """
    Get batch from input_batch_queue and send it to existing model_instance

    Parameters
    ----------
    input_batch_queue:
        Input batch queue, taged queue with batches
    output_batch_queue:
        Where send results
    """
    while True:
        # get models with number of errors > 3
        models_with_errors = model_instances_storage.get_models_with_errors(3)
        for model in models_with_errors:
            source_ids = input_batch_queue.get_source_ids(model)
            for source_id in source_ids:
                try:
                    batch = input_batch_queue.get_nowait(
                        model=model, source_id=source_id
                    )
                except (QueueEmpty, TagDoesNotExists):
                    logger.debug(f"Queue empty for {model=} {source_id=}")
                    logger.debug(input_batch_queue)
                    continue
                response_batch = dm.ResponseBatch.from_minimal_batch_object(
                    batch,
                    error=str(ContainerExited(f"Cannot start model {model.name}")),
                )
                await output_batch_queue.put(response_batch)

        models_by_sources_ids: List[
            Tuple[Optional[str], dm.ModelObject]
        ] = model_instances_storage.get_running_models_with_source_ids()
        tasks = []
        for (source_id, model) in models_by_sources_ids:
            try:
                if not model.stateless:
                    batch = input_batch_queue.get_nowait(
                        model=model, source_id=source_id
                    )
                else:
                    batch = input_batch_queue.get_nowait(model=model)
            except (QueueEmpty, TagDoesNotExists):
                continue
            model_instance = model_instances_storage.get_next_running_instance(
                model, source_id
            )
            if model_instance is None:
                logger.warning(
                    f"Model Instance Storage return None, for {model=} and {source_id=}"
                )
                await input_batch_queue.put(batch)
                continue
            model_instance.lock = True
            logger.info(f"Selected {model_instance}")
            adapter_model_instance = AdapterV1ModelInstance(
                model_instance, input_batch_queue, output_batch_queue
            )
            logger.info(f"Add task for {batch}")
            tasks.append(adapter_model_instance.send(batch))
        if tasks:
            await asyncio.wait(tasks)
        else:
            await asyncio.sleep(5)
