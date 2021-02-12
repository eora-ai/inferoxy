"""
This is test client for batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import sys

import zmq  # type: ignore
import yaml
import numpy as np  # type: ignore

sys.path.append("..")

import src.data_models as dm
from shared_modules.utils import uuid4_string_generator


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
    sock_receiver = ctx.socket(zmq.SUB)
    sock_receiver.bind(config.zmq_output_address)
    sock_receiver.subscribe(b"")

    model_num = int(input(f"Choose model\n1: {stub_model}\n2: {stateful_model}: "))
    if model_num == 1:
        model = stub_model
    else:
        model = stateful_model

    number_of_request = int(input("Write number of requests: "))
    uid_generator = uuid4_string_generator()
    for _ in range(number_of_request):
        request_info = dm.RequestInfo(
            input=np.array(range(10)),
            parameters={},
        )
        req = dm.RequestObject(
            uid=next(uid_generator),
            requests_info=[request_info],
            source_id="test_client_1",
            model=model,
        )
        sock_sender.send_pyobj(req)
    print("Start listenning")
    while True:
        result = sock_receiver.recv_pyobj()
        print(f"Result batch {result}")


if __name__ == "__main__":
    main()
