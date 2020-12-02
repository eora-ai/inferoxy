"""
Store connections for model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import src.data_models as dm


class AdapterModelInstance:
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
        await self.sender.send(AdapterModelInstance.batch_to_v3_format(batch))

    @classmethod
    def batch_to_v3_format(cls, batch: dm.RequestBatch) -> dict:
        """
        Convert batch to v3 format.
        """
        # TODO: recall v3 format
        return {}
