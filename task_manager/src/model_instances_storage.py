"""
This module is storing model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from collections import defaultdict
from typing import Dict, List, Tuple, Optional

from src.receiver_streams_combiner import ReceiverStreamsCombiner
from src.utils.data_transfers import Receiver
import src.data_models as dm


class ModelInstancesStorage:
    """
    This class is store model instance, and process round robin select over it
    """

    def __init__(self, receiver_streams_combiner: ReceiverStreamsCombiner):
        self.model_instances: Dict[
            dm.ModelObject, List[dm.ModelInstance]
        ] = defaultdict(list)
        self.receiver_streams_combiner = receiver_streams_combiner

    def add_model_instance(self, model_instance: dm.ModelInstance):
        self.model_instances[model_instance.model].append(model_instance)
        self.receiver_streams_combiner.add_listener(model_instance.receiver)

    def remove_model_instance(self, model_instance: dm.ModelInstance):
        self.model_instances[model_instance.model].remove(model_instance)
        if not self.model_instances[model_instance.model]:
            del self.model_instances[model_instance.model]
        self.receiver_streams_combiner.remove_listener(model_instance.receiver)

    def get_running_models_with_source_ids(
        self,
    ) -> List[Tuple[Optional[str], dm.ModelObject]]:
        models_with_source_ids: List[Tuple[Optional[str], dm.ModelObject]] = []
        for model in self.model_instances.keys():
            if model.stateless:
                models_with_source_ids.append((None, model))
            else:
                model_with_source_ids = [
                    (model_instance.source_id, model)
                    for model_instance in self.model_instances[model]
                ]
                models_with_source_ids.extend(model_with_source_ids)

        return models_with_source_ids

    def get_next_running_instance(
        self, model: dm.ModelObject, source_ids: Optional[str] = None
    ) -> dm.ModelInstance:
        pass
