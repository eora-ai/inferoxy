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
pip insatll -r requirements-dev.txt
```

### How to run tests
1. Pytest
```bash=
pytest
```
