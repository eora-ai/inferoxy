"""
This is test client for batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import sys

import numpy as np
import zmq
import yaml

sys.path.append("..")

import src.data_models as dm
from src.utils import uuid4_string_generator


stub_model = dm.ModelObject(
    name="stub",
    address="registry.visionhub.ru/models/stub:v3",
    stateless=True,
    batch_size=4,
)

stateful_model = dm.ModelObject(
    name="stateful_stub",
    address="registry.visionhub.ru/models/stateful_stub:v3",
    stateless=False,
    batch_size=4,
)


def main():
    with open("../config.yaml") as f:
        config_dict = yaml.full_load(f)
        config = dm.Config(**config_dict)

    ctx = zmq.Context()
    sock_sender = ctx.socket(zmq.PUB)
    sock_sender.connect(config.zmq_input_address)

    model_num = int(input(f"Choose model\n1: {stub_model}\n2: {stateful_model}: "))
    if model_num == 1:
        model = stub_model
    else:
        model = stateful_model

    number_of_request = int(input(f"Write number of requests: "))
    uid_generator = uuid4_string_generator()
    for _ in range(number_of_request):
        req = dm.RequestObject(
            uid=next(uid_generator),
            inputs=np.array(range(10)),
            source_id="test_client_1",
            parameters={},
            model=model,
        )
        sock_sender.send_pyobj(req)


if __name__ == "__main__":
    main()
