__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import Optional, Union

from pydantic import BaseModel

from shared_modules.data_objects import (
    BaseConfig,
    ModelObject,
)


class DatabaseConfig(BaseModel):
    """
    Config for remote database
    """

    host: str
    port: int
    number: int


class Config(BaseModel):
    address: str
    database: DatabaseConfig
