"""
This module is responsible for receiving data from model instance
"""

__author__ = "Andrey Chertkov"
__name__ = "a.chertkov@eora.ru"

from typing import AsyncIterator


class Receiver:
    def __init__(self):
        pass

    async def sync(self):
        pass

    async def receive(self) -> AsyncIterator[dict]:
        yield {}

    def close(self):
        pass
