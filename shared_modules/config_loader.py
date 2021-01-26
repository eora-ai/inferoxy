"""
This module define useful functions for loading configs
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Type

import yaml

import data_objects as dm


def load_config(config_class: Type[dm.BaseConfig], path: str) -> dm.BaseConfig:
    """
    Base load config
    """
    with open(path, "r") as config_file:
        config_dict = yaml.full_load(config_file)
        return config_class(**config_dict)
