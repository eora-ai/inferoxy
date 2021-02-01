"""
Store connections for model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


from datetime import datetime

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
        await self.sender.send(batch)
        batch.status = dm.Status.SENT_TO_MODEL
        batch.started_at = datetime.now()
        self.model_instance.current_processing_batch = batch
