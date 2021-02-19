# Any image that can run python scripts
FROM python:3.7-slim-buster

# Environment params for runner
ENV dataset_addr=tcp://*:5556
ENV result_addr=tcp://*:5555

# Copy runners and python requirements.txt
COPY requirements.txt /model_base/requirements.txt

# Install python requirements
RUN pip install -r /model_base/requirements.txt

COPY . /model_base
ENV TEST_MODE=0
ENV BATCH_SIZE=1

# Run command for docker container
# PARAMS for `container_runner.py`:
#   '--dataset_addr' - 'Address of socket to connect to the dataset queue'
#   '--result_addr' - 'Address of a socket to connect to the results queue'
#   '--TEST_MODE' - '1 if needed to run in test mode, 0 otherwise'
CMD python -u /model_base/container_runner.py --dataset_addr=${dataset_addr}  \
                                              --result_addr=${result_addr}  \
                                              --test_mode=$TEST_MODE --batch_size=$BATCH_SIZE
