"""
This module is responsible for manage cloud.
Increase, decrease and get operations over model instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import docker  # type: ignore
import random
import yaml
import pathlib

from loguru import logger
from typing import List, Set
from abc import ABC, abstractmethod

import src.data_models as dm
import src.exceptions as exc
from src.utils.data_transfers import Receiver, Sender


class BaseCloudClient(ABC):
    """
    Operation over cloud, Base class needed because want different cloud
    client, for k8s and for docker-compose/docker
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
            Information of the model instance, name of
            the pod/container and address
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
        self.gpu_all = set(config.gpu_all)
        self.gpu_busy: Set[int] = set()

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
            if model.run_on_gpu:
                logger.info(f"This instance {container.name} is running on gpu")
            else:
                logger.info(f"This instance {container.name} is running on cpu")
            model_instance = self.build_model_instance(
                model=model,
                container_name=container.name,
            )
            model_instances.append(model_instance)
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
                gpu_available = self.gpu_all.difference(self.gpu_busy)
                num_gpu = random.sample(gpu_available, 1)[0]
                print("GPU NUMBER: ", num_gpu)
                self.gpu_busy.add(num_gpu)

                # Run container on GPU
                logger.info("Run container on GPU")
                container = self.run_container(
                    image=model.address,
                    on_gpu=True,
                    num_gpu=num_gpu,
                )

                # Construct model instanse
                model_instance = self.build_model_instance(
                    model=model,
                    container_name=container.name,
                    num_gpu=num_gpu,
                )
                return model_instance

            else:
                # Run container on CPU
                logger.info("Run container on CPU")
                container = self.run_container(model.address)

                # Construct model instanse
                model_instance = self.build_model_instance(
                    model=model,
                    container_name=container.name,
                )
                return model_instance

        except docker.errors.APIError:
            raise exc.DockerAPIError()

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop container

        `docker stop`
        """
        try:
            # If run on gpu then remove gpu from busy gpu list
            if model_instance.num_gpu is not None:
                self.gpu_busy.remove(model_instance.num_gpu)

            container = self.client.containers.get(model_instance.container_name)
            container.stop()

        except docker.errors.NotFound:
            raise exc.ContainerNotFound()
        except docker.errors.APIError:
            raise exc.DockerAPIError()

    def run_container(self, image, num_gpu=None, detach=True, on_gpu=False):
        """
        Create and run docker container
        """

        # Run on GPU
        if on_gpu:
            return self.client.containers.run(
                image=image,
                detach=detach,
                runtime="nvidia",
                environment={"GPU_NUMBER": num_gpu},
                ports={
                    "5556/tcp": 5556,
                    "5546/tcp": 5546,
                    "5555/tcp": 5555,
                    "5545/tcp": 5545,
                },
            )

        # Run on CPU
        return self.client.containers.run(
            image=image,
            detach=detach,
            ports={
                "5556/tcp": 5556,
                "5546/tcp": 5546,
                "5555/tcp": 5555,
                "5545/tcp": 5545,
            },
        )

    def build_model_instance(self, model, container_name, lock=False, num_gpu=None):
        """
        Build and return model instance object
        """

        cur_path = pathlib.Path(__file__)
        config_path = cur_path.parent / "utils/data_transfers/zmq-config.yaml"

        with open(config_path) as config_file:
            config_dict = yaml.full_load(config_file)
            config = dm.ZMQConfig(**config_dict)

        # Build addresses
        sender_open_address = f"tcp://{container_name}:5556"
        sender_sync_address = f"tcp://{container_name}:5546"

        receiver_open_address = f"tcp://{container_name}:5555"
        receiver_sync_address = f"tcp://{container_name}:5545"

        # Create sender and receiver
        sender = Sender(
            open_address=sender_open_address,
            sync_address=sender_sync_address,
            config=config,
        )

        receiver = Receiver(
            open_address=receiver_open_address,
            sync_address=receiver_sync_address,
            config=config,
        )

        return dm.ModelInstance(
            model=model,
            sender=sender,
            receiver=receiver,
            lock=lock,
            source_id=None,
            container_name=container_name,
            num_gpu=num_gpu,
        )
