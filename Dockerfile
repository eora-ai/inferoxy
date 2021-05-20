FROM python:3.9


RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

WORKDIR app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf 

# Configs
COPY task_manager/config.yaml /etc/inferoxy/task_manager.yaml
COPY batch_manager/config.yaml /etc/inferoxy/batch_manager.yaml
COPY debatch_manager/config.yaml /etc/inferoxy/debatch_manager.yaml
COPY zmq_bridge/config.yaml /etc/inferoxy/zmq_bridge.yaml
COPY restapi_bridge/config.yaml /etc/inferoxy/restapi_bridge.yaml
COPY grpc_bridge/config.yaml /etc/inferoxy/grpc_bridge.yaml
COPY model_storage/config.yaml /etc/inferoxy/model_storage.yaml
COPY bridges.yaml /etc/inferoxy/bridges.yaml

COPY . .

EXPOSE 7787
EXPOSE 7788
EXPOSE 8000

ENTRYPOINT /app/entrypoint.sh
