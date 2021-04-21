"""
Test for `config_processor` module
"""
import pytest

from src.exceptions import EmptyBridges
from src.config_processor import bridges_to_supervisord
import src.data_models as dm

bridge = dm.BridgeDescription(
    name="zmq_bridge",
    directory="/app/zmq_bridge",
    command="python3 main.py",
    active=True,
)


def test_bridges_to_supervisord_config_with_zero_arguments():
    """
    Test `bridges_to_supervisord_config` with passing zero arguments
    """

    with pytest.raises(EmptyBridges):
        bridges_to_supervisord([])


def test_bridges_to_supervisord_config_with_one_arguments():
    """
    Test `bridges_to_supervisord_config` with passing one element in list
    """

    result = bridges_to_supervisord([bridge])
    assert "# Bridges" in result
    assert f"[program:{bridge.name}]" in result


def test_bridges_to_supervisord_config_with_one_non_active_arguments():
    """
    Test `bridges_to_supervisord_config` with passing one element with `active=False`
    """
    bridge.active = False
    with pytest.raises(EmptyBridges):
        bridges_to_supervisord([bridge])
