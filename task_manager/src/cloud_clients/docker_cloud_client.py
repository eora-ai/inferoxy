"""
This module is responsible for docker based cloud(Actualy it is single machine)
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import random
from typing import List, Set, Optional

import docker  # type: ignore
from loguru import logger

import src.data_models as dm
import src.exceptions as exc
from src.cloud_clients import BaseCloudClient
from src.health_checker.errors import (
    ContainerDoesNotExists,
    ContainerExited,
    HealthCheckError,
)

from shared_modules.utils import uuid4_string_generator


class DockerCloudClient(BaseCloudClient):
    """
    Implementation of docker based cloud
    """

    def __init__(self, config: dm.Config):
        """
        Authorize client
        """
        super().__init__(config)
        self.uid_generator = uuid4_string_generator()
        self.client = docker.DockerClient(base_url="unix://var/run/docker.sock")

        if self.config is None:
            raise exc.CloudClientErrors(
                "Docker config does not provided"
            )  # Make config not optional
        self.config: dm.Config = self.config

        self.docker_config_optional: Optional[dm.DockerConfig] = self.config.docker
        if self.docker_config_optional is None:
            raise exc.CloudClientErrors("Docker config does not provided")
        self.docker_config: dm.DockerConfig = self.docker_config_optional

        try:
            self.client.login(
                username=self.docker_config.login,
                password=self.docker_config.password,
                registry=self.docker_config.registry,
            )
        except:
            logger.critical("Cannot login to Docker registry")
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
                hostname=container.name,
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
        on_gpu = model.run_on_gpu
        num_gpu = None
        if on_gpu:
            # Geneerate gpu available
            gpu_available = self.gpu_all.difference(self.gpu_busy)
            num_gpu = random.sample(gpu_available, 1)[0]
            logger.debug(f"GPU NUMBER: {num_gpu} for {model.name=}")
            self.gpu_busy.add(num_gpu)

        try:
            logger.debug("Run container")
            name = f"{model.name}_{next(self.uid_generator)}"
            container = self.run_container(
                name=name,
                image=model.address,
                on_gpu=on_gpu,
                num_gpu=num_gpu,
            )
            logger.info(f"Container is up: {container}")
        except docker.errors.APIError as exception:
            raise exc.CloudAPIError() from exception

        # Construct model instanse
        model_instance = self.build_model_instance(
            model=model,
            hostname=name,
            num_gpu=num_gpu,
        )
        logger.info(f"Build model instance: {model_instance}")
        return model_instance

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop container

        `docker stop`
        """
        try:
            # If run on gpu then remove gpu from busy gpu list
            if model_instance.num_gpu is not None:
                self.gpu_busy.remove(model_instance.num_gpu)

            logger.debug(f"Stop container {model_instance.hostname}")

            container = self.client.containers.get(model_instance.hostname)
            container.stop()
            container.remove()

        except docker.errors.NotFound as exception:
            raise exc.ContainerNotFound() from exception
        except docker.errors.APIError as exception:
            raise exc.CloudAPIError() from exception

    def run_container(
        self, name: str, image: str, num_gpu=None, detach=True, on_gpu=False
    ):
        """
        Create and run docker container
        """

        s_open_port = self.config.models.ports.sender_open_addr
        r_open_port = self.config.models.ports.receiver_open_addr

        # Run on GPU
        runtime = "runc"
        environment = {
            "dataset_addr": f"tcp://*:{s_open_port}",
            "result_addr": f"tcp://*:{r_open_port}",
        }
        if on_gpu:
            runtime = "nvidia"
            environment["GPU_NUMBER"] = num_gpu

        # Run on CPU
        return self.client.containers.run(
            name=name,
            image=image,
            detach=detach,
            runtime=runtime,
            environment=environment,
            network=self.docker_config.network,
            hostname=name,
        )

    def get_maximum_running_instances(self) -> int:
        return int(self.config.max_running_instances)  # type: ignore

    def is_instance_running(
        self, model_instance: dm.ModelInstance
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        reason: Optional[HealthCheckError] = None
        try:
            container = self.client.containers.get(model_instance.hostname)
        except:
            is_running = False
            reason = ContainerDoesNotExists(
                "Container {model_instance.hostname} does not exists"
            )
            return dm.ReasoningOutput(is_running, reason)
        is_running = container.status == "running"
        if not is_running:
            reason = ContainerExited(
                f"""Container status: {container.status}, last 10 lines of logs:
                {container.logs(tail=10)}"""
            )
        return dm.ReasoningOutput(is_running, reason)
