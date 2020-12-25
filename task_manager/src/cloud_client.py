"""
This module is responsible for manage cloud.
Increase, decrease and get operations over model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import docker  # type: ignore
import sys
from loguru import logger
import random

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
        self.gpu_all = config.gpu_all
        self.gpu_busy: List[int] = []

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
            # TODO: how to show model instance running on gpu
            if model.run_on_gpu:
                logger.info(f"This instance {container.name} is running on gpu")
            else:
                logger.info(f"This instance {container.name} is running on cpu")
            model_instances.append(
                dm.ModelInstance(
                    model=model,
                    source_id=None,
                    sender=Sender(),
                    receiver=Receiver(),
                    lock=False,
                    container_name=container.name,
                )
            )
        return model_instances

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        if not model.run_on_gpu:
            return True
        if len(self.gpu_busy) == len(self.gpu_all):
            return False
        return True

    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        """
        Start instance base on model image

        `docker run`
        """
        try:
            # Pull image
            logger.info("Pull model image")
            self.client.images.pull(model.address)

            if model.run_on_gpu:
                # Geneerate gpu available
                gpu_available = list(set(self.gpu_all) - set(self.gpu_busy))
                num_gpu = random.choice(gpu_available)
                self.gpu_busy.append(num_gpu)

                # Run container
                # TODO: Run on gpu
                # container = self.client.containers.run(
                #     model.address,
                #     detach=True,
                #     # runtime="nvidia",
                # )
                container = self.run_container(model.address)
                # Construct model instanse
                return dm.ModelInstance(
                    model=model,
                    sender=Sender(),
                    receiver=Receiver(),
                    lock=False,
                    source_id=None,
                    container_name=container.name,
                    num_gpu=num_gpu,
                )

            else:
                # Run container on CPU
                logger.info("Run container")
                container = self.run_container(model.address)
                # container = self.client.containers.run(model.address, detach=True)

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
            # If run on gpu then remove gpu from busy gpu list
            if model_instance.num_gpu != 0:
                self.gpu_busy.remove(model_instance.num_gpu)
            container = self.client.containers.get(model_instance.container_name)
            container.stop()
        except docker.errors.NotFound:
            raise RuntimeError("Failed found container")

    def run_container(self, image, detach=True, run_time=None):
        # TODO: add in runtime oprion run on GPU
        return self.client.containers.run(image=image, detach=detach)
