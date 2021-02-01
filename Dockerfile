FROM python:3.9

RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf 

WORKDIR app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["/usr/bin/supervisord"]
