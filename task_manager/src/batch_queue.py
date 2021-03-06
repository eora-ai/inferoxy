"""
This module is responsible for transfer Batches from receiver to process and from process to sender
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import datetime
from asyncio import Queue, QueueEmpty
from typing import Optional, Dict, Tuple, List

from loguru import logger

import src.data_models as dm
from src.exceptions import TagDoesNotExists

QueueSize = int


class InputBatchQueue:
    """
    Set of queues of modeled input batches, between receiver and process
    """

    def __init__(self):
        self.queues: Dict[
            str, Dict[Tuple[Optional[str], dm.ModelObject], (QueueSize, Queue)]
        ] = dict(stateless={}, stateful={})

    def __str__(self) -> str:
        return str(self.queues)

    @staticmethod
    def __prepare_for_put(item: dm.MinimalBatchObject):
        if item.status == dm.Status.ERROR:
            item.retries += 1
        item.queued_at = datetime.datetime.now()
        item.status = dm.Status.IN_QUEUE

    async def put(
        self,
        item: dm.MinimalBatchObject,
    ):
        """
        Put dm.ResponseBatch into queue, save time processing for load analyzer

        Parameters
        ----------
        item:
            dm.MinimalBatchObject item, that will be transformed into RequestBatchObject,
            Set status=created and created_at, this will be saved into queue
        """
        self.__prepare_for_put(item)
        source_id = self.__get_source_id(item)
        queue = self.__select_or_create_queue(item.model, source_id=source_id)
        self.__increase_queue_size(item)
        await queue.put(item)

    def get_source_ids(self, model: dm.ModelObject) -> List[Optional[str]]:
        """
        Return all source ids for model from queues
        """
        if model.stateless:
            return [None]
        try:

            return [source_id for source_id, _ in self.queues["stateful"].keys()]
        except StopIteration:
            return []

    def put_nowait(self, item: dm.MinimalBatchObject):
        """
        Put dm.ResponseBatch into queue, save time processing for load analyzer, not-async method

        Parameters
        ----------
        item:
            dm.MinimalBatchObject item, that will be transformed into RequestBatchObject,
            Set status=created and created_at, this will be saved into queue
        """
        self.__prepare_for_put(item)
        source_id = self.__get_source_id(item)
        queue = self.__select_or_create_queue(item.model, source_id=source_id)
        self.__increase_queue_size(item)
        queue.put_nowait(item)

    @staticmethod
    def __get_source_id(item: dm.MinimalBatchObject) -> Optional[str]:
        if not item.model.stateless:
            return item.source_id
        return None

    def __increase_queue_size(self, batch: dm.MinimalBatchObject):
        """
        Increase size of queue by batch.size
        """
        sub_queues = self.queues["stateless" if batch.model.stateless else "stateful"]
        size, queue = sub_queues[(batch.source_id, batch.model)]
        sub_queues[(batch.source_id, batch.model)] = (size + batch.size, queue)

    def __decrease_queue_size(self, batch: dm.MinimalBatchObject):
        """
        Increase size of queue by batch.size
        """
        sub_queues = self.queues["stateless" if batch.model.stateless else "stateful"]
        size, queue = sub_queues[(batch.source_id, batch.model)]
        sub_queues[(batch.source_id, batch.model)] = (size - batch.size, queue)

    def __select_or_create_queue(
        self, model: dm.ModelObject, source_id: Optional[str] = None
    ) -> Queue:
        queue = self.__select_queue(model, source_id)
        if queue is None:
            queue = self.__create_queue(model, source_id)
        return queue

    def __create_queue(
        self,
        model: dm.ModelObject,
        source_id: Optional[str] = None,
    ) -> Queue:
        queue: Queue = Queue()
        sub_queue = self.queues["stateless" if model.stateless else "stateful"]
        sub_queue[(source_id, model)] = (0, queue)
        return queue

    def __select_queue(
        self,
        model: dm.ModelObject,
        source_id: Optional[str] = None,
    ) -> Optional[Queue]:
        """
        Select queue by model

        Parameters
        ----------
        model:
            Tag of the queue
        """
        try:
            return self.queues["stateless" if model.stateless else "stateful"][
                (source_id, model)
            ][1]
        except KeyError:
            return None

    def __delete_queue(
        self,
        model: dm.ModelObject,
        source_id: Optional[str] = None,
    ):
        try:
            del self.queues["stateless" if model.stateless else "stateful"][
                (source_id, model)
            ]
        except KeyError:
            return

    def get_nowait(
        self,
        model: dm.ModelObject,
        source_id: Optional[str] = None,
    ):
        """
        Get item using get_nowait from queue with model=model,
        Parameters
        ----------
        model:
            model of the queue

        Returns:
            Request Batch object
        """
        queue = self.__select_queue(model, source_id)
        if queue is None:
            raise TagDoesNotExists(f"Tag {(source_id, model)} doesnot exists")
        try:
            batch = queue.get_nowait()
            self.__decrease_queue_size(batch)
        except QueueEmpty as exc:
            self.__delete_queue(model, source_id)
            raise exc
        return batch

    def get_models(self, is_stateless: bool = True) -> List[dm.ModelObject]:
        """
        Return models in the queue
        """
        source_id_models = list(
            self.queues["stateless" if is_stateless else "stateful"].keys()
        )
        return list(map(lambda x: x[1], source_id_models))

    def get_models_with_source_ids(
        self, is_stateless: bool = True
    ) -> List[Tuple[Optional[str], dm.ModelObject]]:
        """
        Return keys, (source_id, model)
        """
        source_id_models = list(
            self.queues["stateless" if is_stateless else "stateful"].keys()
        )
        return source_id_models

    def get_num_requests_in_queue(
        self, model: dm.ModelObject, source_id: Optional[str] = None
    ) -> QueueSize:
        """
        Return number of requests in queue, size of each batch in queue
        """
        sub_queues = self.queues["stateless" if model.stateless else "stateful"]
        return sub_queues[(source_id, model)][0]

    def get_sizes(self) -> Dict[str, Dict[dm.ModelObject, int]]:
        """
        Return number of request in input batch queue
        """
        result: Dict[str, Dict[dm.ModelObject, int]] = {}
        for sub_queue_name in self.queues:
            sub_queue = self.queues[sub_queue_name]
            result[sub_queue_name] = {}
            for source_id, model in sub_queue:
                result[sub_queue_name][model] = sub_queue[(source_id, model)][0]
        return result


class OutputBatchQueue(Queue):
    """
    Queue of output batches, between process and sender
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batches_time_processing = {}
        self.error_batches = []

    async def put(
        self,
        item: dm.ResponseBatch,
    ):
        """
        Put dm.ResponseBatch into queue, save time processing for load analyzer

        Parameters
        ----------
        item:
            dm.ResponseBatch item, that will save into queue, batch status is PROCESSED
        """
        if item.error is not None:
            item.status = dm.Status.FAILED

        if item.mini_batches is not None:
            item.status = dm.Status.PROCESSED
            if item.processed_at is None:
                item.processed_at = datetime.datetime.now()

        logger.debug(f"Response status {item.status}, {item}")
        if (
            item.status == dm.Status.PROCESSED
            and not item.processed_at is None
            and not item.started_at is None
        ):
            processed_time = item.processed_at - item.started_at

            if isinstance(processed_time, datetime.timedelta):
                processed_time_float = processed_time.total_seconds()
            else:
                processed_time_float = processed_time

            self.batches_time_processing[item] = {
                "processing_time": processed_time_float,
                "count": item.size,
            }
        await super().put(item)
        logger.info(
            f"Batch {item.uid} put into the output queue with size {self.qsize()}"
        )
