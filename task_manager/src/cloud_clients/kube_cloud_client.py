"""
This module is responsible for kubernetes based cloud
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import time
import random
from typing import Set, Optional, List

import yaml
from loguru import logger
from kubernetes import client, config  # type: ignore
from kubernetes.client.api import core_v1_api  # type: ignore

import src.data_models as dm
import src.exceptions as exc
from src.cloud_clients import BaseCloudClient
from src.health_checker.errors import (
    PodDoesNotExists,
    PodExited,
    HealthCheckError,
)
from shared_modules.utils import id_generator
from templates import pod_template, pod_gpu_template  # type: ignore


config.load_kube_config()


class KubeCloudClient(BaseCloudClient):
    """
    Implementation of kubernetes based cloud
    """

    def __init__(self, config: dm.Config):
        """
        Set up client
        """
        super().__init__(config)

        if self.config is None:
            raise exc.CloudClientErrors("Config does not provided")
        # Get env variables
        self.host = os.getenv("KUBERNETES_CLUSTER_ADDRESS")
        self.token = os.getenv("KUBERNETES_API_TOKEN")
        self.namespace = os.getenv("NAMESPACE")

        self.gpu_all = set(config.gpu_all)
        self.gpu_busy: Set[int] = set()

        self.kube_config = client.Configuration()
        self.kube_config.host = self.host
        self.kube_config.api_key = {"authorization": f"Bearer {self.token}"}
        self.kube_config.verify_ssl = False

        self.api_client = client.ApiClient(self.kube_config)
        self.api_instance = core_v1_api.CoreV1Api(self.api_client)

        self.id_generator = id_generator()

    def generate_pod_config(self, model: dm.ModelObject):
        """
        Generate pod config from templates for CPU and GPU
        separately
        """
        random_tail = next(self.id_generator)

        # Generate pod name and container name
        pod_name = f"{model.name.replace('_', '-')}-pod-{random_tail}"
        container_name = model.name.replace("_", "-").lower()

        s_open_addr = f"tcp://*:{self.config.models.ports.sender_open_addr}"  # type: ignore
        r_open_addr = f"tcp://*:{self.config.models.ports.receiver_open_addr}"  # type: ignore

        if not model.run_on_gpu:
            # Generate pod config for CPU

            logger.info("Model will run on CPU")
            pod = pod_template.format(
                pod_name=pod_name,
                label=model.name,
                host=container_name,
                container_name=container_name,
                model_link=model.address,
                s_open_address=s_open_addr,
                r_open_addr=r_open_addr,
                batch_size=model.batch_size,
            )
        else:
            # Generate pod config for GPU

            logger.info("Model will run on GPU")
            pod = pod_gpu_template.format(
                pod_name=pod_name,
                label=model.name,
                host=container_name,
                container_name=container_name,
                model_link=model.address,
                s_open_address=s_open_addr,
                r_open_addr=r_open_addr,
                batch_size=model.batch_size,
            )
        pod_manifest = yaml.load(pod)
        return pod_manifest, container_name

    def apply_pod(self, pod_manifest):
        """
        Create pod based on pod configuration
        """
        resp = self.api_instance.create_namespaced_pod(
            body=pod_manifest, namespace=self.namespace
        )
        while True:
            resp = self.api_instance.read_namespaced_pod(
                name=pod_manifest["metadata"]["name"], namespace=self.namespace
            )
            if self.resp.status.phase != "Pending":
                break
            time.sleep(1)
        return resp

    def read_pod(self, pod_name):
        """
        Retrieve data of pod
        """
        try:
            resp = self.api_instance.read_namespaced_pod(
                name=pod_name, namespace=self.namespace
            )
        except Exception:
            return False
        return resp

    def delete_pod(self, pod_name):
        """
        Delete pod
        """
        try:
            resp = self.api_instance.delete_namespaced_pod(
                name=pod_name, namespace=self.namespace, body=client.V1DeleteOptions()
            )
        except Exception:
            return None
        return resp

    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        """
        Get running instances
        """
        model_instances = []

        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for item in ret:
            if item.metadata.label == model.name:
                if model.run_on_gpu:
                    logger.info(
                        f"This instance {item.metadata.pod_name} is running on gpu"
                    )
                else:
                    logger.info(
                        f"This instance {item.metadata.pod_name} is running on cpu"
                    )
                model_instance = self.build_model_instance(
                    model=model,
                    hostname=item.metadata.host,
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
        Create pod based on model image
        """
        num_gpu = None

        if model.run_on_gpu:
            gpu_available = self.gpu_all.difference(self.gpu_busy)
            num_gpu = random.sample(gpu_available, 1)[0]
            logger.info(f"GPU number: {num_gpu}")

        logger.info("Generate pod manifest")
        pod_manifest, container_name = self.generate_pod_config(model)

        logger.info("Apply generated pod")
        self.apply_pod(pod_manifest)

        # Build model instance
        model_instance = self.build_model_instance(
            model=model, hostname=container_name, num_gpu=num_gpu
        )

        return model_instance

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop instance (actually it removes pod by container name)
        """
        if model_instance.num_gpu:
            self.gpu_busy.remove(model_instance.num_gpu)

        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for item in ret:
            if item.metadata.host == model_instance.hostname:
                self.delete_pod(item.metadata.pod_name)

    def get_maximum_running_instances(self) -> int:
        return self.config.max_running_instances  # type: ignore

    def is_instance_running(
        self, model_instance: dm.ModelInstance
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        """
        Check status pod that it is running
        """

        reason: Optional[HealthCheckError] = None

        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for item in ret:
            if item.metadata.host == model_instance.hostname:
                resp = self.read_pod(item.metadata.pod_name)
        else:
            is_running = False
            reason = PodDoesNotExists("Pod {resp.metadata.pod_name} does not exists")
            return dm.ReasoningOutput(is_running, reason)

        is_running = resp.status.phase != "Running"
        if not is_running:
            reason = PodExited(f"""Pod status: {resp.status}""")
        return dm.ReasoningOutput(is_running, reason)
