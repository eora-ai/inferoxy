"""

"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import time
import string
import random
from typing import Set, Optional

import yaml
from loguru import logger
from kubernetes import client, config
from kubernetes.client.api import core_v1_api

import src.data_models as dm
from src.cloud_clients import BaseCloudClient
from src.health_checker.errors import (
    ContainerDoesNotExists,
    ContainerExited,
    HealthCheckError,
)


config.load_kube_config()

# TODO: слишком громозко выглядит
pod_template = """
apiVersion: v1
kind: Pod
metadata:
    name: {pod_name}
spec:
    containers:
        - name: {container_name}
        image: {model_link}
        imagePullPolicy: Always
        env:
            - name: dataset_addr
            value: '{open_addr}'
            - name: dataset_sync_addr
            value: '{sync_addr}'
            - name: result_addr
            value: 'tcp://*:5555'
            - name: result_sync_addr
            value: 'tcp://*:5545'
            - name: BATCH_SIZE
            value: '{batch_size}'
    restartPolicy: Never
    imagePullSecrets:
        - name: visionhub-registry
"""
pod_gpu_template = """
apiVersion: v1
kind: Pod
metadata:
    name: {pod_name}
spec:
    containers:
        - name: {container_name}
        image: {model_link}
        imagePullPolicy: Always
        env:
            - name: dataset_addr
            value: '{open_addr}'
            - name: dataset_sync_addr
            value: '{sync_addr}'
            - name: result_addr
            value: 'tcp://*:5555'
            - name: result_sync_addr
            value: 'tcp://*:5545'
            - name: CUDA_VISIBLE_DEVICES
            value: '{gpu_index}'
            - name: BATCH_SIZE
            value: '{batch_size}'
        resources:
            limits:
                nvidia.com/gpu: 1
    restartPolicy: Never
    imagePullSecrets:
        - name: visionhub-registry
"""


class KubeCloudClient(BaseCloudClient):
    def __init__(self, config: dm.Config):
        super().__init__(config)

        # Get env variables
        self.host = os.getenv(["KUBERNETES_CLUSTER_ADDRESS"])
        self.token = os.getenv(["KUBERNETES_API_TOKEN"])
        self.namespace = os.getenv(["NAMESPACE"])

        self.gpu_all = set(config.gpu_all)
        self.gpu_busy: Set[int] = set()

        self.kube_config = client.Configuration()
        self.kube_config.host = self.host
        self.kube_config.api_key = {"authorization": "Bearer " + self.token}
        self.kube_config.verify_ssl = False

        self.api_client = client.ApiClient(self.kube_config)
        self.api_instance = core_v1_api.CoreV1Api(self.api_client)

    def generate_pod_config(self, model: dm.ModelObject, num_gpu):
        random_tail = self.id_generator()
        pod_name = f"{model.name.replace('_', '-')}-pod-" + random_tail
        container_name = model.name.replace("_", "-").lower() + "-" + random_tail

        # TODO:можно ли использовать порты receiver'a???
        r_open_port = self.config.models.ports.receiver_open_addr
        r_sync_port = self.config.models.ports.receiver_sync_addr

        sync_addr = f"tcp://*:{r_sync_port}"
        open_addr = f"tcp://*:{r_open_port}"

        if num_gpu is None:
            logger.info("Model will run on CPU")
            pod = pod_template.format(
                pod_name=pod_name,
                container_name=container_name,
                model_link=model.address,
                open_addr=open_addr,
                sync_addr=sync_addr,
                batch_size=model.batch_size,
            )
        else:
            logger.info("Model will run on GPU")
            pod = pod_gpu_template.format(
                pod_name=pod_name,
                container_name=container_name,
                model_link=model.address,
                gpu_index=num_gpu,
                open_addr=open_addr,
                sync_addr=sync_addr,
                batch_size=model.batch_size,
            )
        pod_manifest = yaml.load(pod)
        return {
            "manifest": pod_manifest,
            "pod_name": pod_name,
            "container_name": container_name,
        }

    def id_generator(self, size=6, chars=string.ascii_lowercase):
        return "".join(random.choice(chars) for _ in range(size))

    def apply_pod(self, pod_manifest):
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
        try:
            resp = self.api_instance.read_namespaced_pod(
                name=pod_name, namespace=self.namespace
            )
        except Exception:
            return False
        return resp

    def delete_pod(self, pod_name):
        try:
            resp = self.api_instance.delete_namespaced_pod(
                name=pod_name, namespace=self.namespace, body=client.V1DeleteOptions()
            )
        except Exception:
            return None
        return resp

    def get_running_instances(self, model: dm.ModelObject) -> List[dm.ModelInstance]:
        model_instances = []
        pass

    def can_create_instance(self, model: dm.ModelObject) -> bool:
        if not model.run_on_gpu:
            return True
        if len(self.gpu_busy) == len(self.gpu_all):
            return False
        return True

    def start_instance(self, model: dm.ModelObject) -> dm.ModelInstance:
        num_gpu = None

        if model.run_on_gpu:
            gpu_available = self.gpu_all.difference(self.gpu_busy)
            num_gpu = random.sample(gpu_available, 1)[0]
            logger.info(f"GPU number: {num_gpu}")

        logger.info("Generate pod manifest")
        data = self.generate_pod_config(model, num_gpu)
        pod_manifest = data["manifest"]
        container_name = data["container_name"]
        pod_name = data["pod_name"]

        logger.info("Apply generated pod")
        self.apply_pod(pod_manifest)
        model_instance = super().build_model_instance(
            model=model, hostname=container_name, num_gpu=num_gpu
        )
        return model_instance, pod_name

    def stop_instance(self, pod_name):
        pass

    def get_maximum_running_instances(self) -> int:
        return 20  # TODO: replce magic number

    def is_instance_running(
        self, model_instance: dm.ModelInstance, pod_name: str
    ) -> dm.ReasoningOutput[bool, HealthCheckError]:
        reason: Optional[HealthCheckError] = None
        try:
            resp = self.read_pod(pod_name)
        except:
            is_running = False
            reason = ContainerDoesNotExists(
                "Container {model_instance.hostname} does not exists"
            )
            return dm.ReasoningOutput(is_running, reason)

        is_running = resp.status.phase != "Running"
        if not is_running:
            reason = ContainerExited(f"""Podr status: {resp.status}""")
        return dm.ReasoningOutput(is_running, reason)
