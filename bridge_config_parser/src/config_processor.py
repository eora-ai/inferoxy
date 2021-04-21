"""
Main functions that transforms bridges -> supervisord_config
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import Iterable

import src.data_models as dm
from src.exceptions import EmptyBridges


def bridges_to_supervisord(bridges: Iterable[dm.BridgeDescription]) -> str:
    """
    Convert list of bridge description into supervisord config

    Parameters
    ----------
    bridges:
        list of bridge descriptions

    Returns
    -------
        Supervisord config in string
    """
    bridges_config = "\n".join(map(bridge_to_supervisord, bridges))
    if not bridges_config:
        raise EmptyBridges("There are no bridges")

    return "\n\n# Bridges\n\n" + "\n".join(map(bridge_to_supervisord, bridges)) + "\n"


def bridge_to_supervisord(bridge: dm.BridgeDescription) -> str:
    """
    Convert single bridge into supervisord entry

    Parameters
    ----------
    bridge:
        bridge description

    Returns
    -------
        string in format of supervisord.conf if `bridge.active`.
        Example:
        ```
        [program:zmq_bridge]
        directory=/app/zmq_bridge
        command=/bin/bash -c "python3 main.py"
        stdout_logfile=/dev/fd/1
        stdout_logfile_maxbytes=0
        redirect_stderr=true
        ```
    """
    if not bridge.active:
        return ""

    supervisord_config = f"""[program:{bridge.name}]
directory={bridge.directory}
command=/bin/bash -c "{bridge.command}"
stdout_logfile=/dev/fd/1
stdout_logfile_maxbytes=0
redirect_stderr=true"""
    return supervisord_config
