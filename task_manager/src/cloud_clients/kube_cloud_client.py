"""
This module is responsible for kubernetes based cloud
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import time
import asyncio
import concurrent.futures
from typing import Optional, List

import yaml
from loguru import logger
from kubernetes import client  # type: ignore
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
from .templates import pod_template, pod_gpu_template  # type: ignore


class KubeCloudClient(BaseCloudClient):
    """
    Implementation of kubernetes based cloud
    """

    def __init__(self, config: dm.Config):
        """
        Set up client
        """
        super().__init__(config)

        # Get env variables
        if isinstance(self.config.cloud_client, dm.KubeConfig):
            self.kube_config = self.config.cloud_client
            self.host = self.kube_config.address
            self.token = self.kube_config.token
            self.namespace = self.kube_config.namespace
        else:
            raise ValueError("Config cloud_client is not KubeConfig")

        self.auth_config = client.Configuration()
        self.auth_config.host = self.host
        self.auth_config.api_key = {"authorization": f"Bearer {self.token}"}
        self.auth_config.verify_ssl = False

        self.api_client = client.ApiClient(self.auth_config)
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

        s_open_addr = f"tcp://*:{self.config.models.ports.sender_open_addr}"
        r_open_addr = f"tcp://*:{self.config.models.ports.receiver_open_addr}"

        if not model.run_on_gpu:
            logger.info("Model will run on CPU")
            template = pod_template
        else:
            logger.info("Model will run on GPU")
            template = pod_gpu_template
        pod = template.format(
            pod_name=pod_name,
            label=model.name,
            host=container_name,
            container_name=container_name,
            model_link=model.address,
            s_open_addr=s_open_addr,
            r_open_addr=r_open_addr,
            batch_size=model.batch_size,
        )
        pod_manifest = yaml.load(pod)
        return pod_manifest, pod_name

    def apply_pod(self, pod_manifest):
        """
        Create pod based on pod configuration
        """

        resp = self.api_instance.create_namespaced_pod(
            body=pod_manifest, namespace=self.namespace
        )
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < self.kube_config.create_timeout:
            resp = self.api_instance.read_namespaced_pod(
                name=pod_manifest["metadata"]["name"], namespace=self.namespace
            )
            if resp.status.phase != "Pending":
                break
            time.sleep(1)
            current_time = time.time()
        else:
            self.delete_pod(pod_manifest["metadata"]["name"])
            raise exc.CannotCreatePod("Cannot create a pod. Timeout error")
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

    def read_logs(self, pod_name, length=10):
        try:
            resp = self.api_instance.read_namespaced_pod_log(
                name=pod_name, namespace=self.namespace, tail_lines=length
            )
        except Exception:
            return ""
        return resp

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        return True

    async def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        """
        Create pod based on model image
        """

        logger.info("Generate pod manifest")
        pod_manifest, _ = self.generate_pod_config(model)

        logger.info("Apply generated pod")
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            resp = await loop.run_in_executor(executor, self.apply_pod, pod_manifest)
        pod_ip = resp.status.pod_ip

        # Build model instance
        model_instance = self.build_model_instance(
            model=model,
            name=pod_manifest["metadata"]["name"],
            hostname=pod_ip,
        )

        return model_instance

    def stop_instance(self, model_instance: dm.ModelInstance):
        """
        Stop instance (actually it removes pod by container name)
        """
        self.delete_pod(model_instance.name)

    def get_maximum_running_instances(self) -> int:
        return self.config.max_running_instances  # type: ignore

    def is_instance_running(
        self, model_instance: dm.ModelInstance
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        """
        Check status pod that it is running
        """

        reason: Optional[HealthCheckError] = None
        resp = self.read_pod(model_instance.name)
        #    is_running = False
        #    reason = PodDoesNotExists("Pod {resp.metadata.pod_name} does not exists")
        #    return dm.ReasoningOutput(is_running, reason)

        is_running = resp.status.phase == "Running"
        if not is_running:
            logger.warning(f"Pod status {resp.status.phase}")
            logs = self.read_logs(model_instance.name, length=10)
            reason = PodExited(f"Pod logs : {logs}")
        return dm.ReasoningOutput(is_running, reason)
