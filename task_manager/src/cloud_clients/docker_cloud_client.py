"""
This module is responsible for docker based cloud(Actualy it is single machine)
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from typing import List, Set, Optional
import random

import docker  # type: ignore
from loguru import logger

import src.data_models as dm
import src.exceptions as exc
from src.cloud_clients import BaseCloudClient
from src.utils.data_transfers import Receiver, Sender
from src.health_checker.errors import (
    ContainerDoesNotExists,
    ContainerExit,
    HealthCheckError,
)


class DockerCloudClient(BaseCloudClient):
    """
    Implementation of docker based cloud
    """

    def __init__(self, config: dm.Config):
        """
        Authorize client
        """
        super().__init__(config)
        self.client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        if self.config is None or self.config.docker is None:
            raise exc.CloudClientErrors("Docker config does not provided")
        self.client.login(
            username=self.config.docker.login,
            password=self.config.docker.password,
            registry=self.config.docker.registry,
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
        try:
            # Pull image
            logger.info("Pull model image")
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
                    hostname=container.name,
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
                    hostname=container.name,
                )
                return model_instance

        except docker.errors.APIError as exception:
            raise exc.CloudAPIError() from exception

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop container

        `docker stop`
        """
        try:
            # If run on gpu then remove gpu from busy gpu list
            if model_instance.num_gpu is not None:
                self.gpu_busy.remove(model_instance.num_gpu)

            container = self.client.containers.get(model_instance.hostname)
            container.stop()
            container.remove()

        except docker.errors.NotFound as e:
            raise exc.ContainerNotFound() from e
        except docker.errors.APIError as e:
            raise exc.DockerAPIError() from e

    def run_container(self, image, num_gpu=None, detach=True, on_gpu=False):
        """
        Create and run docker container
        """

        s_open_port = self.config.models.ports.sender_open_addr
        s_sync_port = self.config.models.ports.sender_sync_addr
        r_open_port = self.config.models.ports.receiver_open_addr
        r_sync_port = self.config.models.ports.receiver_sync_addr

        # Run on GPU
        runtime = "runc"
        environment = {
            "dataset_addr": f"tcp://*:{s_open_port}",
            "dataset_sync_addr": f"tcp://*:{s_sync_port}",
            "result_addr": f"tcp://*:{r_open_port}",
            "result_sync_addr": f"tcp://*:{r_sync_port}",
        }
        if on_gpu:
            runtime = "nvidia"
            environment["GPU_NUMBER"] = num_gpu

        # Run on CPU
        return self.client.containers.run(
            image=image,
            detach=detach,
            runtime=runtime,
            environment=environment,
            ports={
                str(s_open_port): s_open_port,
                str(s_sync_port): s_sync_port,
                str(r_open_port): r_open_port,
                str(r_sync_port): r_sync_port,
            },
        )

    def build_model_instance(self, model, hostname, lock=False, num_gpu=None):
        """
        Build and return model instance object
        """

        s_open_port = self.config.models.ports.sender_open_addr
        s_sync_port = self.config.models.ports.sender_sync_addr
        r_open_port = self.config.models.ports.receiver_open_addr
        r_sync_port = self.config.models.ports.receiver_sync_addr

        sender_open_address = f"tcp://localhost:{s_open_port}"
        sender_sync_address = f"tcp://localhost:{s_sync_port}"

        receiver_open_address = f"tcp://localhost:{r_open_port}"
        receiver_sync_address = f"tcp://localhost:{r_sync_port}"

        # Create sender and receiver
        sender = Sender(
            open_address=sender_open_address,
            sync_address=sender_sync_address,
            config=self.config.models.zmq_config,
        )

        receiver = Receiver(
            open_address=receiver_open_address,
            sync_address=receiver_sync_address,
            config=self.config.models.zmq_config,
        )

        return dm.ModelInstance(
            model=model,
            sender=sender,
            receiver=receiver,
            lock=lock,
            source_id=None,
            hostname=hostname,
            num_gpu=num_gpu,
            running=True,
        )

    def get_maximum_running_instances(self) -> int:
        return 20  # TODO: replce magic number

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
            reason = ContainerExit(
                f"""Container status: {container.status}, last 10 lines of logs:
                {container.logs(tail=10)}"""
            )
        return dm.ReasoningOutput(is_running, reason)
