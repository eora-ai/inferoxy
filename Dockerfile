FROM python:3.9


RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor

WORKDIR app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf 
COPY . .

EXPOSE 7787
EXPOSE 7788

CMD ["/usr/bin/supervisord"]
