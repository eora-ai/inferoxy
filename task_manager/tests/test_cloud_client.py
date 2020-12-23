"""
Test cloud client
"""
import sys
import yaml
import pytest
import time

sys.path.append("..")

from src.cloud_client import DockerCloudClient

import src.data_models as dm


model_object_fail = dm.ModelObject(
    name="fail", address="akdfjka", stateless=True, batch_size=24
)
model_object_pass = dm.ModelObject(
    name="run", address="nginx", stateless=True, batch_size=24
)


def test_image_doesnt_exist():
    """
    Test function start_instance()
    Throw exceprion RuntimeError -> image does not exist
    """
    with open("../config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    with pytest.raises(RuntimeError) as exc:
        docker_client.start_instance(model_object_fail)
    assert "Image not found" in str(exc.value)


def run():
    with open("../config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    docker_client.start_instance(model_object_pass)


def test_stop_container():
    with open("../config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    model_instance = docker_client.start_instance(model_object_pass)
    time.sleep(10)
    docker_client.stop_instance(model_instance)
    # TODO: think about how to check that container is stoped


if __name__ == "__main__":
    test_stop_container()
