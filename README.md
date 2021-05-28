# Inferoxy documentation

[[_TOC_]]

## What is it?

Inferoxy is a service for quickly deploying and using machine learning models.

## Why use it?

You should use it if:
- You want to simplify deploying machine learning models to production, everything you need is to build a Docker image with your model and push it into our public registry
- You have only one machine for inference or you have a cluster you can run Inferoxy for inferencing.
- Automatic batching
- Model versioning

## Alternatives

There are several alternatives:
- triton
- mlflow
- airflow
- kfserving

The detailed comparison you can find [here](comparisons)

## Requirements
You can run Inferoxy locally on a single machine or [k8s](https://kubernetes.io/) cluster. 
For run Inferoxy, you should have a minimum **4GB RAM**. 

## Basic commands

## Local run
To run locally you should use Inferoxy docker image. Last version you can find [here](https://gitlab.com/eora/data-lab/visionhub/inferoxy/-/releases)
```bash
docker pull public.registry.visionhub.ru/inferoxy:v1.0.4
```
After image is pulled we need to make basic configuration using .env file
```env
# .env
CLOUD_CLIENT=docker
TASK_MANAGER_DOCKER_CONFIG_NETWORK=inferoxy
MODEL_STORAGE_DATABASE_HOST=redis
MODEL_STORAGE_DATABASE_PORT=6379
MODEL_STORAGE_DATABASE_NUMBER=0
LOGGING_LEVEL=INFO
```
The next step is to create `inferoxy` docker network.
```bash
docker network create inferoxy
```
Now we should run Redis in this network. Redis is needed to store information about models.
```bash
docker run --network redis --name redis redis:latest 
```
Create `models.yaml` file with simple set of models. You can read about `models.yaml` [here](models_yaml) 
```yaml
stub:
  address: public.registry.visionhub.ru/models/stub:v5
  batch_size: 256
  run_on_gpu: False
  stateless: True
```

Now we can start inferoxy
```bash
docker run --env-file .env.dev 
	-v /var/run/docker.sock:/var/run/docker.sock \
	-p 7787:7787 -p 7788:7788 -p 8000:8000 -p 8698:8698\
	--name inferoxy --rm \
	--network inferoxy \
	-v $(shell pwd)/models.yaml:/etc/inferoxy/models.yaml \
	public.registry.visionhub.ru/inferoxy:${INFEROXY_VERSION}
```

## Next
- [Detailed overiew](detailed_overview)
- [Advanced configuration](configuration)
- [Deploy on k8s](deploy_on_k8s)
