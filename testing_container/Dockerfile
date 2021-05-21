FROM python:3.9

WORKDIR app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT /app/entrypoint.sh
