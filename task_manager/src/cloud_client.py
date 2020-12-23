"""
This module is responsible for manage cloud.
Increase, decrease and get operations over model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import docker
import sys
from loguru import logger

from abc import ABC, abstractmethod
from typing import List

sys.path.append("..")

import src.data_models as dm
from src.utils.data_transfers import Receiver, Sender


class BaseCloudClient(ABC):
    """
    Operation over cloud, Base class needed because want different cloud client, for k8s and for docker-compose/docker
    """

    @abstractmethod
    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        """
        Get all running model instances by model

        Parameters
        ----------
        model:
            Model object, need to get name of the model
        """

    @abstractmethod
    def can_create_instance(self, model: dm.ModelObject) -> bool:
        """
        Check, if there are a space/instances for new model instances

        Parameters
        ----------
        model:
            Model object, need to get name of the model
        """

    @abstractmethod
    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        """
        Start a model instance

        Parameters
        ----------
        model:
            Model object
        """

    @abstractmethod
    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop a model instance
        Parameters
        ----------
        model_instance:
            Information of the model instance, name of the pod/container and address
        """


class DockerCloudClient(BaseCloudClient):
    """
    Implementation of docker based cloud
    """

    def __init__(self, config: dm.Config):
        """
        Authorize client
        """
        self.client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        self.client.login(
            username=config.docker_login,
            password=config.docker_password,
            registry=config.docker_registry,
        )

    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        """
        Get running instances

        `docker ps`
        """
        containers = self.client.containers.list()
        if len(containers) == 0:
            return []

        model_instances = []
        for container in containers:
            # TODO: заглушка Recevier and Sender
            model_instances.append(
                dm.ModelInstance(
                    model=model,
                    source_id=None,
                    sender=Sender,
                    receiver=Receiver,
                    lock=False,
                    container_name=container.name,
                )
            )
        return model_instances

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        if not model.on_gpu:
            return True
        # TODO: check available gpu

    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        """
        Start instance base on model image

        `docker run`
        """
        try:
            # Pull image
            logger.info("Pull model image")
            self.client.images.pull(model.address)

            if model.on_gpu:
                # TODO: run container on gpu
                pass

            # Run container
            logger.info("Run container")
            container = self.client.containers.run(model.address, detach=True)

            # Construct model instanse
            return dm.ModelInstance(
                model=model,
                sender=Sender(),
                receiver=Receiver(),
                lock=False,
                source_id=None,
                container_name=container.name,
            )
        except docker.errors.APIError:
            raise RuntimeError("Image not found")

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop container

        `docker stop`
        """
        try:
            container = self.client.containers.get(model_instance.container_name)
            container.stop()
        except docker.errors.NotFound:
            raise RuntimeError("Failed found container")
