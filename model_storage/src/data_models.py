__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys
import pathlib
from dataclasses import dataclass

from pydantic_yaml import YamlModel

from shared_modules.data_objects import (
    BaseConfig,
    ModelObject,
)


class DatabaseConfig(YamlModel):
    """
    Config for remote database
    """

    host: str
    port: int
    db_num: int


class Config(YamlModel):
    address: str
