"""
This module is responsible for transfer Batches from receiver to process and from process to sender
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from asyncio import Queue, QueueEmpty
from typing import Optional, Dict, Set
import datetime

import src.data_models as dm
from src.exceptions import TagDoesNotExists


class InputBatchQueue:
    """
    Set of queues of taged input batches, between receiver and process
    """

    def __init__(self):
        self.queues: Dict[dm.ModelObject, Queue] = dict()
        self.tags: Set[dm.ModelObject] = set()

    async def put(self, item: dm.MinimalBatchObject, tag: dm.ModelObject):
        """
        Put ResponseBatch into queue, save time processing for load analyzer

        Parameters
        ----------
        item:
            MinimalBatchObject item, that will transform into RequestBatchObject,
            Set status=created and created_at, that will save into queue
        """
        batch_object = dm.RequestBatch.from_minimal_batch_object(
            item, created_at=datetime.datetime.now(), status=dm.Status.CREATED
        )
        queue = self.__select_queue(tag)
        if queue is None:
            queue = self.__create_queue(tag)
        await queue.put(batch_object)

    def __create_queue(self, tag: dm.ModelObject) -> Queue:
        self.tags.add(tag)
        queue: Queue = Queue()
        self.queues[tag] = queue
        return queue

    def __select_queue(self, tag: dm.ModelObject) -> Optional[Queue]:
        """
        Select queue by tag

        Parameters
        ----------
        tag:
            Tag of the queue
        """
        if tag in self.tags:
            return self.queues[tag]
        return None

    def get_nowait(self, tag: dm.ModelObject):
        """
        Get item using get_nowait from queue with tag=tag,
        Parameters
        ----------
        tag:
            tag of the queue

        Returns:
            Request Batch object
        """
        queue = self.__select_queue(tag)
        if queue is None:
            raise TagDoesNotExists(f"Tag {tag} doesnot exists")
        try:
            batch = queue.get_nowait()
        except QueueEmpty as exc:
            self.tags.remove(tag)
            raise exc
        return batch


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
        Put ResponseBatch into queue, save time processing for load analyzer

        Parameters
        ----------
        item:
            ResponseBatch item, that will save into queue, batch status is DONE
        """
        if (
            item.status == dm.Status.DONE
            and not item.done_at is None
            and not item.started_at is None
        ):
            self.batches_time_processing[item] = item.done_at - item.started_at
        else:
            self.error_batches.append(item)
        item.queued_at = datetime.datetime.now()
        await super().put(item)
