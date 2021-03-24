"""
Test admin API
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"
import json

from pytest import fixture
from fastapi.testclient import TestClient

from src.admin_api import app  # type: ignore
from src.admin_api import get_connection  # type: ignore
from src.connector import Connector  # type: ignore
from src.database import MockRedis  # type: ignore


@fixture
def db_fixture():
    test_model = {
        "address": "test_address",
        "stateless": True,
        "batch_size": 256,
        "run_on_gpu": False,
    }
    mock_redis = MockRedis()
    connector = Connector(mock_redis)
    connector.database.set("test_model", json.dumps(test_model))
    yield connector


@fixture
def client(db_fixture) -> TestClient:
    def _get_db_override():
        return db_fixture

    app.dependency_overrides[get_connection] = _get_db_override
    return TestClient(app)


def test_get_model(client: TestClient):
    response = client.get("/models/test_model")
    assert response.status_code == 200
    assert response.json()["name"] == "test_model"


def test_create_model(client: TestClient):
    test_model = {
        "name": "another_test_model",
        "address": "another_test_address",
        "stateless": True,
        "batch_size": 256,
        "run_on_gpu": False,
    }

    response = client.post("/models", json=test_model)
    assert response.status_code == 200
    assert response.json() == test_model


def test_delete_model(client: TestClient):

    response = client.delete("/models/test_model")
    assert response.status_code == 200


def test_get_not_exist_model(client: TestClient):
    response = client.get("/models/kjgnvzdfk")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model with this slug does not exist"}


def test_delete_not_exist_model(client: TestClient):
    response = client.delete("/models/jadfg")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model with this slug does not exist"}


def test_update_model(client: TestClient):

    response = client.patch(
        "/models/test_model", json={"stateless": False, "batch_size": 128}
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "test_model",
        "address": "test_address",
        "stateless": False,
        "batch_size": 128,
        "run_on_gpu": False,
    }


def test_update_get_model(client: TestClient):
    response = client.patch(
        "/models/test_model",
        json={"stateless": False, "batch_size": 128, "run_on_gpu": True},
    )
    model_update = response.json()
    assert response.status_code == 200

    response = client.get("/models/test_model")
    assert response.status_code == 200
    model_get = response.json()

    assert model_update == model_get
