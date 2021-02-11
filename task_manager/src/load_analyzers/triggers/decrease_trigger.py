"""
DecreaseTrigger class
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Optional

from . import Trigger
import src.data_models as dm


class DecreaseTrigger(Trigger):
    """
    Stop instance, when applied
    """

    def apply(self) -> Optional[dm.ModelInstance]:
        """
        Stop instance
        """
        if self.cloud_client is None:
            return None

        if self.model_instance:
            self.cloud_client.stop_instance(self.model_instance)

        return self.model_instance
