__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Any, Optional

import numpy as np  # type: ignore
from pydantic import BaseModel

from shared_modules.data_objects import (
    RequestObject,
    RequestInfo,
    ResponseObject,
    ResponseInfo,
    InputModel,
    RequestModel,
    OutputModel,
    ResponseModel,
)


class Config(BaseModel):
    """
    Config object
    """

    batch_manager_address: str
    debatch_manager_address: str
    model_storage_address: str
