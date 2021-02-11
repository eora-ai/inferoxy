"""
IncreaseTrigger class
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Optional

from . import Trigger
import src.data_models as dm


class IncreaseTrigger(Trigger):
    """
    Create new instance, when applied
    """

    def apply(self) -> Optional[dm.ModelInstance]:
        """
        Start a new instance
        """
        if self.cloud_client is None or self.model is None:
            return None

        if self.cloud_client.can_create_instance(self.model):
            return self.cloud_client.start_instance(self.model)

        return None
