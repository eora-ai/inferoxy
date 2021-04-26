"""
Data models that used for bridge config parser
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List
from pathlib import Path

from pydantic import BaseModel


class BridgeDescription(BaseModel):
    """
    Description of bridge

    Parameters
    ----------
    name:
        Name of the bridge
    directory:
        Directory in where `command` will be executed
    command:
        Command that should be executed to start the bridge
    active:
        Is a bridge active, should we start a `command`?
    """

    name: str
    directory: str
    command: str
    active: bool


class Config(BaseModel):
    """
    Config of the bridge
    """

    bridges: List[BridgeDescription]
    supervisord_config_path: Path
