"""
This templates for generation kubernetes pod
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

# lable is model name
# host is model instance host (actually is container name)
pod_template = """
apiVersion: v1
kind: Pod
metadata:
    name: {pod_name}
    label: {label}
    host: {host}
spec:
    containers:
        - name: {container_name}
        image: {model_link}
        imagePullPolicy: Always
        env:
            - name: dataset_addr
            value: '{s_open_addr}'
            - name: result_addr
            value: '{r_open_addr}'
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
    label: {label}
    host: {host}
spec:
    containers:
        - name: {container_name}
        image: {model_link}
        imagePullPolicy: Always
        env:
            - name: dataset_addr
            value: '{s_open_addr}'
            - name: result_addr
            value: '{r_open_addr}'
            - name: BATCH_SIZE
            value: '{batch_size}'
        resources:
            limits:
                nvidia.com/gpu: 1
    restartPolicy: Never
    imagePullSecrets:
        - name: visionhub-registry
"""
