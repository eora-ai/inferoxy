"""
This module is responsible for listen the receiver and conver response to ResponseBatch
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import asyncio
from typing import AsyncIterator, Union, Dict, Optional

from aiostream import stream  # type: ignore

from src.batch_queue import OutputBatchQueue
from src.utils.data_transfers.receiver import Receiver
import src.data_models as dm


class ResponseToBatch:

    BREAK = "BREAK"

    def __init__(self, output_batch_queue: OutputBatchQueue):
        self.output_batch_queue = output_batch_queue
        self.sources: Dict[Optional[Receiver], AsyncIterator[Union[str, dict]]] = {
            None: self.check_source_interaptor()
        }
        self.combined_streams = stream.merge(*self.sources.values())
        self.sourcers_updated = False

    def add_listener(
        self, receiver: Receiver, async_response_iter: AsyncIterator[dict]
    ) -> None:
        self.sources[receiver] = async_response_iter
        self.combined_streams = stream.merge(*self.sources.values())
        self.sourcers_updated = True

    def remove_listener(self, receiver: Receiver):
        del self.sources[receiver]
        self.sourcers_updated = True

    async def check_source_interaptor(self) -> AsyncIterator[str]:
        while True:
            await asyncio.sleep(0.001)
            if self.sourcers_updated:
                yield self.BREAK
                self.sourcers_updated = False

    async def converter(self):
        while True:
            with self.combined_streams.stream() as stream:
                async for response in stream:
                    if response == self.BREAK:
                        break
                    self.output_batch_queue.put(self._make_batch(response))

    def _make_batch(self, result: dict) -> dm.ResponseBatch:
        # TODO: recall v3 format
        return dm.ResponseBatch(**result)
