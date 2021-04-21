__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import List, Any, Optional

import numpy as np  # type: ignore
from pydantic import BaseModel
from pydantic_yaml import YamlModel  # type: ignore

from shared_modules.data_objects import (
    RequestObject,
    RequestInfo,
    ResponseObject,
    ResponseInfo,
    InputModel,
    RequestModel,
    OutputModel,
    ResponseModel,
    # For test
    ModelObject,
    BatchMapping,
)


class Config(YamlModel):
    """
    Config object
    """

    batch_manager_address: str
    debatch_manager_address: str
    model_storage_address: str
    listen_address: str
    send_address: str
