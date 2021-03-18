# Inferoxy

It is a service for quickly deploying and using machine learning models.


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

### How to run tests
1. Pytest
```bash=
pytest
```


### How to run test client for batch manager

Run batch manager
```bash=
cd batch_manager
python main.py
```
Run client
```bash=
cd batch_manager/test_client
python main.py
```
Check that db contains BatchMapping
```bash=
python db.py
```

### How to run docker

Create `.env` file with variables
* `CLOUD_CLIENT=docker`
* `DOCKER_REGISTRY`
* `DOCKER_LOGIN`
* `DOCKER_PASSWORD`
* `DB_HOST`
* `DB_PORT`
* `LOGGING_LEVEL`

Run commands:
```
docker build . -t inferoxy:v1
docker run --env-file .env -v /var/run/docker.sock:/var/run/docker.sock inferoxy:v1
```
