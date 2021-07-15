"""
This module is responsible for listen the receiver and conver response to dm.ResponseBatch
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import Union, Dict, Optional, Tuple, List, Awaitable

from loguru import logger

import src.data_models as dm
from src.batch_queue import OutputBatchQueue
from src.utils.data_transfers.receiver import BaseReceiver


class ReceiverStreamsCombiner:
    """
    Combine receiver streams and put result into output_batch_queue

    Parameters
    ----------
    output_batch_queue:
        Queue where will be placed result, dm.ResponseBatch objects.
    """

    def __init__(self, output_batch_queue: OutputBatchQueue):
        self.output_batch_queue = output_batch_queue
        self.tasks: Dict[
            BaseReceiver, Awaitable[Tuple[BaseReceiver, dm.ResponseBatch]]
        ] = {}
        self.running = True
        self.receivers_to_delete: List[BaseReceiver] = []

    def add_listener(self, receiver: BaseReceiver) -> None:
        """
        Add receiver listener to sourcers
        """
        logger.debug("Add listener")

        self.tasks[receiver] = asyncio.create_task(
            self.__converter_function(receiver, receiver.receive())
        )

    @staticmethod
    async def __converter_function(
        receiver: BaseReceiver,
        future: Awaitable[dm.ResponseBatch],
    ) -> Tuple[BaseReceiver, dm.ResponseBatch]:
        batch = await future
        return (receiver, batch)

    async def remove_listener(self, receiver: BaseReceiver):
        """
        Remove receiver listener from combining sourcers
        """
        logger.debug("Try to remove listener")
        self.receivers_to_delete.append(receiver)
        logger.debug("Listener is removed")

    def stop(self):
        """
        Stop converter
        """
        logger.warning("Receiver stream combiner will be stoped")
        self.running = False

    async def converter(self):
        """
        Main method, receive dm.ResponseBatch, and put it to output_batch_queue
        """
        while self.running:
            await asyncio.sleep(0.1)
            tasks_to_process = self.tasks.values()
            if not tasks_to_process:
                continue
            done, _ = await asyncio.wait(
                tasks_to_process, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                result = task.result()

                receiver, batch = result
                if batch is not None:
                    await self.output_batch_queue.put(batch)
                    model_instance = receiver.get_model_instance()
                    model_instance.release()

                if receiver in self.receivers_to_delete:
                    logger.debug("Remove listener")
                    self.tasks.pop(receiver)
                    receiver.close()

                if receiver in self.tasks:
                    self.tasks[receiver] = asyncio.create_task(
                        self.__converter_function(receiver, receiver.receive())
                    )
