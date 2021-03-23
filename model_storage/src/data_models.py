__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys
import pathlib
from dataclasses import dataclass

from shared_modules.data_objects import (
    BaseConfig,
    ModelObject,
)


@dataclass
class DatabaseConfig(BaseConfig):
    """
    Config for remote database
    """

    host: str
    port: int
    db_num: int
