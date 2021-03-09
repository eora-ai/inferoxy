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
COPY listener/config.yaml /etc/inferoxy/listener.yaml
COPY model_storage/config.yaml /etc/inferoxy/model_storage.yaml

COPY . .

EXPOSE 7787
EXPOSE 7788

CMD ["/usr/bin/supervisord"]
