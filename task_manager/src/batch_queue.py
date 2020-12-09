"""
This module is responsible for transfer Batches from receiver to process and from process to sender
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from asyncio import Queue, QueueEmpty
from typing import Optional, Dict, Tuple
import datetime

import src.data_models as dm
from src.exceptions import TagDoesNotExists


class InputBatchQueue:
    """
    Set of queues of taged input batches, between receiver and process
    """

    def __init__(self):
        self.queues: Dict[
            str, Dict[Tuple[Optional[str], dm.ModelObject], Queue]
        ] = dict(stateless={}, stateful={})

    async def put(
        self,
        item: dm.MinimalBatchObject,
        tag: dm.ModelObject,
        is_stateless: bool = True,
        source_id: Optional[str] = None,
    ):
        """
        Put ResponseBatch into queue, save time processing for load analyzer

        Parameters
        ----------
        item:
            MinimalBatchObject item, that will be transformed into RequestBatchObject,
            Set status=created and created_at, this will be saved into queue
        """
        item.queued_at = datetime.datetime.now()
        item.status = dm.Status.IN_QUEUE
        queue = self.__select_queue(tag, is_stateless, source_id)
        if queue is None:
            queue = self.__create_queue(tag, is_stateless, source_id)
        await queue.put(item)

    def __create_queue(
        self,
        tag: dm.ModelObject,
        is_stateless: bool = True,
        source_id: Optional[str] = None,
    ) -> Queue:
        queue: Queue = Queue()
        sub_queue = self.queues["stateless" if is_stateless else "stateful"]
        sub_queue[(source_id, tag)] = queue
        return queue

    def __select_queue(
        self,
        tag: dm.ModelObject,
        is_stateless: bool = True,
        source_id: Optional[str] = None,
    ) -> Optional[Queue]:
        """
        Select queue by tag

        Parameters
        ----------
        tag:
            Tag of the queue
        """
        try:
            return self.queues["stateless" if is_stateless else "stateful"][
                (source_id, tag)
            ]
        except KeyError:
            return None

    def __delete_queue(
        self,
        tag: dm.ModelObject,
        is_stateless: bool = True,
        source_id: Optional[str] = None,
    ):
        try:
            del self.queues["stateless" if is_stateless else "stateful"][
                (source_id, tag)
            ]
        except KeyError:
            return

    def get_nowait(
        self,
        tag: dm.ModelObject,
        is_stateless: bool = True,
        source_id: Optional[str] = None,
    ):
        """
        Get item using get_nowait from queue with tag=tag,
        Parameters
        ----------
        tag:
            tag of the queue

        Returns:
            Request Batch object
        """
        queue = self.__select_queue(tag, is_stateless, source_id)
        if queue is None:
            raise TagDoesNotExists(f"Tag {(source_id, tag)} doesnot exists")
        try:
            batch = queue.get_nowait()
        except QueueEmpty as exc:
            self.__delete_queue(tag, is_stateless, source_id)
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
            ResponseBatch item, that will save into queue, batch status is PROCESSED
        """
        if (
            item.status == dm.Status.PROCESSED
            and not item.processed_at is None
            and not item.started_at is None
        ):
            self.batches_time_processing[item] = {
                "processing_time": item.processed_at - item.started_at,
                "count": item.size,
            }
        else:
            self.error_batches.append(item)
        await super().put(item)
