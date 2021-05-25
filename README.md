# Inferoxy

It is a service for quickly deploying and using machine learning models.


## Environment variables

* `CLOUD_CLIENT`
* `DOCKER_REGISTRY`
* `DOCKER_LOGIN`
* `DOCKER_PASSWORD`
* `DOCKER_NETWORK`
* `DB_HOST`
* `DB_PORT`
* `DB_NUMBER`
* `LOGGING_LEVEL`
* `KUBERNETES_CLUSTER_ADDRESS`
* `KUBERNETES_API_TOKEN`
* `NAMESPACE`


## Development setup

0. Install [pyenv](https://github.com/pyenv/pyenv)
1. Create a virtualenv
```bash=
pyenv install 3.9.0
pyenv virtualenv 3.9.0 inferoxy
pyenv activate inferoxy
```
2. Install requirements
```bash=
pip install -r requirements.txt
```
3. Install dev requirements
```bash=
pip install -r requirements-dev.txt
```

### How to run docker

Run commands:
```
export INFEROXY_VERSION=<version>
make
```

## Production setup

### Inferoxy config
<p>
<details>
<summary>Click this to view code.</summary>

<pre><code>
apiVersion: v1
  kind: ConfigMap
metadata:
  name: inferoxy-config
  namespace: production
data:
  CLOUD_CLIENT: kube
  KUBERNETES_CLUSTER_ADDRESS: https://714547A05AE210C2F1ECF0EB65D809E2.gr7.eu-west-1.eks.amazonaws.com
  NAMESPACE: production
  DB_HOST: redis
  DB_PORT: "6379"
  DB_NUMBER: "6"
  LOGGING_LEVEL: WARNING
</code></pre>

</details>
</p>


### Inferoxy deployment
<p>
<details>
<summary>Click this to view code.</summary>

<pre><code>
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inferoxy-deployment
  labels:
    app: inferoxy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: inferoxy
  template:
    metadata:
      labels:
        app: inferoxy
    spec:
      nodeSelector:
        cpu-instance: "TRUE"
      containers:
      - env:
        - name: KUBERNETES_API_TOKEN
          valueFrom:
              secretKeyRef:
                name: service-account-token
                key: token
        envFrom:
          - configMapRef:
              name: inferoxy-config
        volumeMounts:
        - name: inferoxy-config-volume
          mountPath: /etc/inferoxy/
        image: registry.visionhub.ru/inferoxy:v0.0.6
        imagePullPolicy: Always
        name: inferoxy
        ports:
        - containerPort: 7788
        - containerPort: 7787
        - containerPort: 8000
        resources:
          limits:
            memory: 2Gi
      restartPolicy: Always
      imagePullSecrets:
      - name: visionhub-registry
      volumes:
      - name: inferoxy-config-volume
        configMap:
          name: inferoxy-persistent-config
</code></pre>

</details>
</p>

### Inferoxy persistent config
<p>
<details>
<summary>Click this to view code.</summary>

<pre><code>
apiVersion: v1
kind: ConfigMap
metadata:
  name: inferoxy-persistent-config
data:
  task_manager.yaml: |
    zmq_input_address: "ipc:///tmp/batch_manager/result"
    zmq_output_address: "ipc:///tmp/task_manager/result"
    gpu_all: [1]
    max_running_instances: 10

    health_check:
      connection_idle_timeout: 120

    load_analyzer:
      sleep_time: 3 
      trigger_pipeline:
        max_model_percent: 60
      running_mean:
        min_threshold: 5
        max_threshold: 10
        window_size: 20
      stateful_checker:
        keep_model: 30

    models:
      ports:
        sender_open_addr: 5556
        receiver_open_addr: 5546
      zmq_config:
        sndhwm: 10
        rcvhwm: 10
        sndtimeo: 3600000 # ms
        rcvtimeo: 3 # ms

    kube:
      create_timeout: 300 # seconds
  batch_manager.yaml: |
    zmq_input_address: "ipc:///tmp/batch_manager/input"
    zmq_output_address: "ipc:///tmp/batch_manager/result"
    db_file: "/tmp/batch_manager/db"
    create_db_file: True
    send_batch_timeout: 0.1
  debatch_manager.yaml: |
    zmq_input_address: "ipc:///tmp/task_manager/result"
    zmq_output_address: "ipc:///tmp/debatch_manager/result"
    db_file: "/tmp/batch_manager/db"
    create_db_file: true
    send_batch_mapping_timeout: 0.3
  listener.yaml: |
    batch_manager_input_address: ipc:///tmp/batch_manager/input
    debatch_manager_output_address: ipc:///tmp/debatch_manager/result
    model_storage_address: ipc:///tmp/model_storage

    zmq_python:
      listen_address: "tcp://*:7787"
      send_address: "tcp://*:7788"
  model_storage.yaml: |
    address: "ipc:///tmp/model_storage"
</code></pre>

</details>
</p>


## How to run tests
1. Batch manager
```bash=
pytest batch_manager
```

2. Debatch manager
```bash=
pytest debatch_manager
```

3. Model storage
```bash=
pytest model_storage
```

4. Task manager
```bash=
pytest task_manager
```

## How to config

1. Batch manager

Create file `batch_manager/config.yaml` with this parameters:
```yaml=
zmq_input_address: "ipc:///tmp/batch_manager/input"
zmq_output_address: "ipc:///tmp/batch_manager/result"
db_file: "/tmp/batch_manager/db"
create_db_file: true
send_batch_timeout: 0.1
```

2. Debatch manager
Create file `debatch_manager/config.yaml` with this parameters:

```yaml=
zmq_input_address: "ipc:///tmp/task_manager/result"
zmq_output_address: "ipc:///tmp/debatch_manager/result"
db_file: "/tmp/batch_manager/db"
create_db_file: true
send_batch_mapping_timeout: 0.3
```

3. Task manager
Create file `task_manager/config.yaml` with this parameters:

```yaml=
zmq_input_address: "ipc:///tmp/batch_manager/result"
zmq_output_address: "ipc:///tmp/task_manager/result"
gpu_all: [1]
max_running_instances: 10

health_check:
  connection_idle_timeout: 10

load_analyzer:
  sleep_time: 3 
  trigger_pipeline:
    max_model_percent: 60
  running_mean:
    min_threshold: 5
    max_threshold: 10
    window_size: 20
  stateful_checker:
    keep_model: 30

models:
  ports:
    sender_open_addr: 5556
    receiver_open_addr: 5546
  zmq_config:
    sndhwm: 10
    rcvhwm: 10
    sndtimeo: 3600000 # ms
    rcvtimeo: 3 # ms

kube:
  create_timeout: 300 # seconds
```

4. Listener
Create file `listener/config.yaml` with this parameters:

```yaml=
batch_manager_input_address: ipc:///tmp/batch_manager/input
debatch_manager_output_address: ipc:///tmp/debatch_manager/result
model_storage_address: ipc:///tmp/model_storage

zmq_python:
  listen_address: "tcp://*:7787"
  send_address: "tcp://*:7788"
```

5. Model base
Create file `model_base/config.yaml` with this parameters:

```yaml=
zmq_sndhwm: 10
zmq_rcvhwm: 10
zmq_sndtimeo: 3600000
zmq_rcvtimeo: 3600000
```

6. Model storage
Create file `model_storage/config.yaml` with this parameters:

```yaml=
address: "ipc:///tmp/model_storage"
```

## How to start managers

1. Batch manager
```bash=
cd batch_manager
python3 main.py
```

2. Debatch manager
```bash=
cd debatch_manager
python3 main.py
```

3. Task manager
```bash=
cd task_manager
python3 main.py
```

4. Listener
```bash=
cd listener
python3 main.py
```

5. Model storage
```bash=
cd model_storage
python3 main.py
```

--------------------------

### To start model storage admin API

```bash=
uvicorn src.admin_api:app
```
