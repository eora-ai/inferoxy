__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from typing import Optional, Union

from pydantic_yaml import YamlModel     # type: ignore

from shared_modules.data_objects import (
    BaseConfig,
    ModelObject,
)


class DatabaseConfig(YamlModel):
    """
    Config for remote database
    """

    host: str
    port: Union[int, str]
    number: Union[int, str]


class Config(YamlModel):
    address: str
    database: Optional[DatabaseConfig] = None
