"""
This module is storing model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from loguru import logger
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

import src.data_models as dm
from src.utils.data_transfers import Receiver
from src.receiver_streams_combiner import ReceiverStreamsCombiner


class ModelInstancesStorage:
    """
    This class is store model instance, and process round robin select over it
    """

    def __init__(self, receiver_streams_combiner: ReceiverStreamsCombiner):
        self.model_instances: Dict[
            dm.ModelObject, List[dm.ModelInstance]
        ] = defaultdict(list)
        self.indexes: Dict[dm.ModelObject, int] = defaultdict(int)
        self.receiver_streams_combiner = receiver_streams_combiner

    def add_model_instance(self, model_instance: dm.ModelInstance):
        self.model_instances[model_instance.model].append(model_instance)
        self.receiver_streams_combiner.add_listener(model_instance.receiver)

    async def remove_model_instance(self, model_instance: dm.ModelInstance):
        try:
            self.model_instances[model_instance.model].remove(model_instance)
        except ValueError as exc:
            logger.error(exc)
        if not self.model_instances[model_instance.model]:
            del self.model_instances[model_instance.model]
        model_instance.receiver.close()
        model_instance.sender.close()
        await self.receiver_streams_combiner.remove_listener(model_instance.receiver)

    def get_model_instance(
        self, model: dm.ModelObject, source_id: Optional[str] = None
    ) -> Optional[dm.ModelInstance]:
        for model_instance in self.model_instances[model]:
            if model_instance.source_id == source_id:
                return model_instance
        return None

    def get_model_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        """
        Return list of model instances for model
        """
        return self.model_instances.get(model, [])

    def set_source_id(self, model: dm.ModelObject, source_id: str):
        """
        Set source_id to model_instance that have source_id == None
        """
        model_instance = self.get_model_instance(model, source_id=None)
        if model_instance is None:
            return
        model_instance.source_id = source_id

    def get_running_models_with_source_ids(
        self, is_stateless: Optional[bool] = None
    ) -> List[Tuple[Optional[str], dm.ModelObject]]:
        models_with_source_ids: List[Tuple[Optional[str], dm.ModelObject]] = []
        for model in self.model_instances.keys():
            if model.stateless and is_stateless in (None, True):
                models_with_source_ids.append((None, model))
            elif not model.stateless and is_stateless in (None, False):
                temp_model_instances = [
                    (model_instance.source_id, model)
                    for model_instance in self.model_instances[model]
                ]
                models_with_source_ids.extend(temp_model_instances)

        return models_with_source_ids

    def get_running_models(self) -> List[dm.ModelObject]:
        """
        Return models, that have at least one running model instance
        """
        return list(self.model_instances.keys())

    def get_number_of_running_instancse(self) -> Dict[dm.ModelObject, int]:
        """
        Return number of running models
        """
        result = defaultdict(int)
        for model in self.model_instances:
            result[model] = len(self.model_instances[model])
        return result

    def get_not_locked_model_instances(
        self, model: dm.ModelObject
    ) -> List[dm.ModelInstance]:
        """
        Get model instances where lock=False
        """
        model_instances = self.get_model_instances(model)
        not_locked = list(filter(lambda mi: not mi.lock, model_instances))
        return not_locked

    def get_all_model_instances(self) -> List[dm.ModelInstance]:
        """
        Get all model instances in the model instance storage
        """
        model_instances = []
        for model_instances_ in self.model_instances.values():
            model_instances.extend(model_instances_)
        return model_instances

    def get_next_running_instance(
        self, model: dm.ModelObject, source_id: Optional[str] = None
    ) -> Optional[dm.ModelInstance]:
        model_instances = self.model_instances[model]

        if source_id is not None:
            # For stateful models
            for model_instance in model_instances:
                if model_instance.source_id == source_id:
                    return model_instance
            return None

        # For stateless models
        index = self.indexes[model]
        self.indexes[model] = (index + 1) % len(self.model_instances[model])
        return self.model_instances[model][index]
