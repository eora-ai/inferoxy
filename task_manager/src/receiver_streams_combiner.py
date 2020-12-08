"""
This module is responsible for listen the receiver and conver response to ResponseBatch
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import AsyncIterator, Union, Dict, Optional

from aiostream.stream import merge  # type: ignore

from src.batch_queue import OutputBatchQueue
from src.utils.data_transfers.receiver import Receiver
import src.data_models as dm


class ReceiverStreamsCombiner:
    """
    Combine receiver streams and put result into output_batch_queue

    Parameters
    ----------
    output_batch_queue:
        Queue where will be placed result, ResponseBatch objects.
    """

    BREAK = "BREAK"

    def __init__(self, output_batch_queue: OutputBatchQueue):
        self.output_batch_queue = output_batch_queue
        self.sources: Dict[Optional[Receiver], AsyncIterator[Union[str, dict]]] = {
            None: self.check_source_interaptor()
        }
        self.combined_streams = merge(*self.sources.values())
        self.sourcers_updated = False

    def add_listener(self, receiver: Receiver) -> None:
        """
        Add receiver listener to sourcers
        """
        self.sources[receiver] = receiver.receive()
        self.combined_streams = merge(*self.sources.values())
        self.sourcers_updated = True

    def remove_listener(self, receiver: Receiver):
        """
        Remove receiver listener from combining sourcers
        """
        del self.sources[receiver]
        self.sourcers_updated = True

    async def check_source_interaptor(self) -> AsyncIterator[str]:
        """
        Interaptor async iterator, needed to recombine receiver streamms.
        """
        while True:
            await asyncio.sleep(0.001)
            if self.sourcers_updated:
                yield self.BREAK
                self.sourcers_updated = False

    async def converter(self):
        """
        Main method, convert dict to ResponseBatch, and put it to output_batch_queue
        """
        while True:
            with self.combined_streams.stream() as stream:
                async for response in stream:
                    if response == self.BREAK:
                        break
                    self.output_batch_queue.put(self._make_batch(response))

    @classmethod
    def _make_batch(cls, result: dict) -> dm.ResponseBatch:
        """
        Batch from dict format
        """
        return dm.ResponseBatch(**result)
