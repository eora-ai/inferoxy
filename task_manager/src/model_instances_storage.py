"""
This module is storing model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from collections import defaultdict
from typing import Set, Dict, AsyncIterator, List

from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.utils.data_transfers import Receiver
import src.data_models as dm


class ModelInstancesStorage:
    """
    This class is store model instance, and process round robin select over it
    """

    def __init__(self, receiver_streams_combiner: ReceiverStreamsCombiner):
        self.models: Set[dm.ModelObject] = set()
        self.model_instances: Dict[
            dm.ModelObject, List[dm.ModelInstance]
        ] = defaultdict(list)
        self.receiver_streams_combiner = receiver_streams_combiner

    def add_model_instance(self, model_instance: dm.ModelInstance):
        self.models.add(model_instance.model)
        self.model_instances[model_instance.model].append(model_instance)
        self.receiver_streams_combiner.add_listener(
            model_instance.receiver, model_instance.receiver.receive()
        )

    def remove_model_instance(self, model_instance: dm.ModelInstance):
        if model_instance.model not in self.models:
            raise ValueError(f"{model_instance=} not in storage")
        self.model_instances[model_instance.model].remove(model_instance)
        self.receiver_streams_combiner.remove_listener(model_instance.receiver)
        if not self.model_instances[model_instance.model]:
            self.models.remove(model_instance.model)

    def get_running_models(self) -> List[dm.ModelObject]:
        return list(self.models)

    def get_next_running_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        pass
