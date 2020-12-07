"""
Store connections for model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


from dataclasses import asdict

import src.data_models as dm


class AdapterV1ModelInstance:
    """
    Make adapter between BatchRequest and model v3 format
    """

    def __init__(self, model_instance: dm.ModelInstance):
        self.model_instance = model_instance
        self.sender = model_instance.sender

    async def send(self, batch: dm.RequestBatch):
        """
        Parse batches into v3 model request
        """
        await self.sender.send(AdapterV1ModelInstance.batch_to_send_dict(batch))

    @classmethod
    def batch_to_send_dict(cls, batch: dm.RequestBatch) -> dict:
        """
        Convert batch to dict format.
        """
        return asdict(batch)
