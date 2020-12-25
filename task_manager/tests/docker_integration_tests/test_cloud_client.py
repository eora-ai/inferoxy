"""
Test cloud client
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import yaml
import pytest
import time

sys.path.append("../..")

from src.cloud_client import DockerCloudClient

from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

import src.data_models as dm


model_object_fail = dm.ModelObject(
    name="fail",
    address="akdfjka",
    stateless=True,
    batch_size=24,
)
model_object_pass = dm.ModelObject(
    name="run",
    address="nginx",
    stateless=True,
    batch_size=24,
)

model_object_gpu = dm.ModelObject(
    name="run", address="nginx", stateless=True, batch_size=24, run_on_gpu=True
)

model_instance_fail = dm.ModelInstance(
    model=model_object_pass,
    source_id=None,
    sender=Sender(),
    receiver=Receiver(),
    lock=False,
    container_name="kdjfskalf",
)


def test_image_doesnt_exist():
    """
    Test function start_instance() on CPU
    Throw exceprion RuntimeError -> image does not exist
    """
    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    with pytest.raises(RuntimeError) as exc:
        docker_client.start_instance(model_object_fail)
    assert "Image not found" in str(exc.value)


def test_stop_container():
    """
    Test function stop_instance() on model running on gpu
    """
    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    model_instance = docker_client.start_instance(model_object_gpu)

    # Get old data
    old_busy = docker_client.gpu_busy
    num_gpu = model_instance.num_gpu

    # Check that gpu inside busy gpu list
    inside_busy = ""
    if num_gpu in docker_client.gpu_busy:
        inside_busy = "gpu inside"

    assert inside_busy == "gpu inside"

    time.sleep(5)
    docker_client.stop_instance(model_instance)
    assert len(old_busy) == len(docker_client.gpu_busy)

    if num_gpu not in docker_client.gpu_busy:
        inside_busy = "gpu not inside"

    assert inside_busy == "gpu not inside"


def test_list_containers():
    """
    Test function get_running_instances()
    """
    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    model_instance = docker_client.start_instance(model_object_pass)

    model_instances = docker_client.get_running_instances(model_object_pass)

    assert model_instance.container_name == model_instances[0].container_name


def test_can_run_on_gpu():
    """
    Test function can_create_instance()
    """

    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    can_create = docker_client.can_create_instance(model_object_gpu)
    test = ""
    if can_create:
        test = "CAN"
    assert test == "CAN"


def test_run_on_gpu():
    """
    Test function start_instance() on GPU
    """

    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    docker_client.start_instance(model_object_gpu)

    assert len(docker_client.gpu_busy) == 1


def test_cannot_run_gpu():
    """
    Test function can_create_instance() return False
    """

    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)

    for _ in range(4):
        docker_client.start_instance(model_object_gpu)

    test = ""
    if not docker_client.can_create_instance(model_object_gpu):
        test = "CANNOT"

    assert test == "CANNOT"


def test_failed_stop():
    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    with pytest.raises(RuntimeError) as exc:
        docker_client.stop_instance(model_instance_fail)
    assert "Failed found container" in str(exc.value)


if __name__ == "__main__":
    test_run_on_gpu()
