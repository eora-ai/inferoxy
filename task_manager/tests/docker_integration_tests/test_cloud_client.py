"""
Test cloud client
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import os
import time
import pathlib

import yaml
import pytest

import src.exceptions as ex
import src.data_models as dm
from src.cloud_clients import DockerCloudClient
from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver


model_object_fail = dm.ModelObject(
    name="fail",
    address="akdfjka",
    stateless=True,
    batch_size=24,
)
model_object_pass = dm.ModelObject(
    name="stub",
    address="nginx",
    stateless=True,
    batch_size=24,
)

model_object_gpu = dm.ModelObject(
    name="stub",
    address="nginx",
    stateless=True,
    batch_size=24,
    run_on_gpu=True,
)

model_instance_fail = dm.ModelInstance(
    model=model_object_pass,
    source_id=None,
    sender=BaseSender(),
    receiver=BaseReceiver(),
    lock=False,
    hostname="kdjfskalf",
    running=False,
)

cur_path = pathlib.Path(__file__)
config_path = cur_path.parent.parent.parent / "config.yaml"

with open(config_path) as config_file:
    config_dict = yaml.full_load(config_file)
    config = dm.Config(**config_dict)
    config.docker = dm.DockerConfig(
        registry=os.environ.get("DOCKER_REGISTRY", ""),
        login=os.environ.get("DOCKER_LOGIN", ""),
        password=os.environ.get("DOCKER_PASSWORD", ""),
    )


def test_image_doesnt_exist():
    """
    Test function start_instance() on CPU
    Throw exceprion RuntimeError -> image does not exist
    """

    docker_client = DockerCloudClient(config)
    with pytest.raises(ex.CloudAPIError):
        docker_client.start_instance(model_object_fail)


def test_stop_container():
    """
    Test function stop_instance() on model running on gpu
    """
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

    docker_client.client.containers.prune()


def test_list_containers():
    """
    Test function get_running_instances()
    """

    docker_client = DockerCloudClient(config)
    model_instance = docker_client.start_instance(model_object_pass)

    model_instances = docker_client.get_running_instances(model_object_pass)

    assert model_instance.hostname == model_instances[0].hostname

    for item in model_instances:
        container = docker_client.client.containers.get(item.hostname)
        container.remove(force=True)


def test_can_run_on_gpu():
    """
    Test function can_create_instance()
    """

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

    docker_client = DockerCloudClient(config)
    model_instance = docker_client.start_instance(model_object_gpu)

    assert len(docker_client.gpu_busy) == 1
    c = docker_client.client.containers.get(model_instance.hostname)
    c.remove(force=True)


def test_cannot_run_gpu():
    """
    Test function can_create_instance() return False
    """

    docker_client = DockerCloudClient(config)

    model_instance = docker_client.start_instance(model_object_gpu)
    test = ""
    if not docker_client.can_create_instance(model_object_gpu):
        test = "CANNOT"

    assert test == "CANNOT"
    c = docker_client.client.containers.get(model_instance.hostname)
    c.remove(force=True)


def test_failed_stop():
    docker_client = DockerCloudClient(config)
    with pytest.raises(ex.ContainerNotFound):
        docker_client.stop_instance(model_instance_fail)
