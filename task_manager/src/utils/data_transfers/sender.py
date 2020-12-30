"""
This module is responsible for sending data to model instance
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


class Sender:
    def __init__(self):
        pass

    async def sync(self):
        pass

    async def send(self, obj: object):
        pass

    def close(self):
        pass
