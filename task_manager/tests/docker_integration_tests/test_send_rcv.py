"""
Test cloud client with sender and receiver
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


import sys
import yaml
import pytest
import time

from src.cloud_clients import DockerCloudClient

from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

import src.data_models as dm


model_object_pass = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v4",
    stateless=True,
    batch_size=24,
)


def main():
    with open("../../../task_manager/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.Config(**config_dict)

    docker_client = DockerCloudClient(config)
    docker_client.start_instance(model_object_pass)
    print("Container is running")


if __name__ == "__main__":
    main()
