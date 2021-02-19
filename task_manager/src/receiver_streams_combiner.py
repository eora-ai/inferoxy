"""
This module is responsible for listen the receiver and conver response to dm.ResponseBatch
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import AsyncIterator, Union, Dict, Optional, Tuple, List

from aiostream.stream import merge  # type: ignore
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

    BREAK = "BREAK"

    def __init__(self, output_batch_queue: OutputBatchQueue):
        self.output_batch_queue = output_batch_queue
        self.sources: Dict[
            Optional[BaseReceiver],
            Union[
                AsyncIterator[Union[str, Tuple[BaseReceiver, dm.ResponseBatch]]],
                AsyncIterator[str],
            ],
        ] = {None: self.check_source_interaptor()}
        self.sources_to_remove: List[
            Union[
                AsyncIterator[Union[str, Tuple[BaseReceiver, dm.ResponseBatch]]],
                AsyncIterator[str],
            ]
        ] = []
        self.combined_streams = merge(*self.sources.values())
        self.running = True
        self.sourcers_updated = False

    def add_listener(self, receiver: BaseReceiver) -> None:
        """
        Add receiver listener to sourcers
        """
        logger.debug("Add listener")

        async def __converter_function(
            iterator: AsyncIterator[dm.ResponseBatch],
        ) -> AsyncIterator[Union[str, Tuple[BaseReceiver, dm.ResponseBatch]]]:
            async for batch in iterator:
                if batch == 0:
                    yield self.BREAK
                yield (receiver, batch)

        self.sources[receiver] = __converter_function(receiver.receive())
        self.combined_streams = merge(*self.sources.values())
        self.sourcers_updated = True

    async def remove_listener(self, receiver: BaseReceiver):
        """
        Remove receiver listener from combining sourcers
        """
        logger.debug("Try to remove listener")

        try:
            receiver_iterator = self.sources.pop(receiver)
            self.sources_to_remove.append(receiver_iterator)
        except KeyError as exc:
            logger.error(exc)
        self.combined_streams = merge(*self.sources.values())
        self.sourcers_updated = True
        logger.info("Listener is removed")

    async def check_source_interaptor(self) -> AsyncIterator[str]:
        """
        Interaptor async iterator, needed to recombine receiver streamms.
        """
        while True:
            await asyncio.sleep(0.001)
            if self.sourcers_updated:
                self.sourcers_updated = False
                logger.info("Sources updated")
                yield self.BREAK
                self.sources_to_remove = []

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
            async with self.combined_streams.stream() as stream:
                async for response in stream:
                    logger.info(f"Receive from model {response}")
                    if response == self.BREAK:
                        break
                    receiver = response[0]
                    batch = response[1]
                    model_instance = receiver.get_model_instance()
                    model_instance.lock = False
                    model_instance.current_processing_batch = None

                    await self.output_batch_queue.put(batch)
