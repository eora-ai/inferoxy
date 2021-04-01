__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import Optional

from pydantic_yaml import YamlModel     # type: ignore

from shared_modules.data_objects import (
    BaseConfig,
    ModelObject,
)


class DatabaseConfig(YamlModel):
    """
    Config for remote database
    """

    host: Optional[str] = None
    port: Optional[int] = None
    number: Optional[int] = None


class Config(YamlModel):
    address: Optional[str] = None
    database: Optional[DatabaseConfig] = None
