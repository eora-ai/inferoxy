"""
Test of connector
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import src.data_models as dm  # type: ignore
from src.connector import Connector  # type: ignore


def test_build_model():
    model_params = {
        "name": "stub",
        "link": "address",
        "batch_size": 1,
        "supported_modes": [1, 3],
    }

    model = Connector.build_model_object(model_params)
    expected_model = dm.ModelObject(
        name="stub",
        address="address",
        stateless=True,
        batch_size=1,
        run_on_gpu=False,
    )

    assert model.name == expected_model.name
    assert model.address == expected_model.address
    assert model.stateless == expected_model.stateless
    assert model.batch_size == expected_model.batch_size
