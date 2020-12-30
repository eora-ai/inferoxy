"""
This module is responsible for docker based cloud(Actualy it is single machine)
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Set
import random

import docker  # type: ignore

from loguru import logger

from src.utils.data_transfers import Receiver, Sender
import src.exceptions as exc
import src.data_models as dm

from src.cloud_clients import BaseCloudClient


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
            # TODO: заглушка Recevier and Sender
            # TODO: how to show model instance running on gpu
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
            raise exc.ImageNotFound()

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
            )

        # Run on CPU
        return self.client.containers.run(image=image, detach=detach)

    def build_model_instance(self, model, container_name, lock=False, num_gpu=None):
        """
        Build and return model instance object
        """
        return dm.ModelInstance(
            model=model,
            sender=Sender(),
            receiver=Receiver(),
            lock=lock,
            source_id=None,
            container_name=container_name,
            num_gpu=num_gpu,
        )
