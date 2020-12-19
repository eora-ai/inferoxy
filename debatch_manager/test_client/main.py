"""
Test client for debatcher manager
"""
import sys

import zmq
import yaml
import numpy as np
import src.data_models as dm
import uuid
from typing import Generator
from shared_modules.data_objects import (
    ModelObject,
    ResponseBatch,
    Status,
)

sys.path.append('..')

stateful_model = ModelObject(
    name="stateful_stub",
    address="registry.visionhub.ru/models/stateful_stub:v3",
    stateless=False,
    batch_size=4,
)


# TODO: Move to shared module file batch_manager.src.utils
def uuid4_string_generator() -> Generator[str, None, None]:
    """
    Make from uuid4 generator of random strings

    Returns
    -------
    Generator[str]
        Infinite random strings generator
    """
    while True:
        uid = uuid.uuid4()
        yield str(uid)


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

    uid_generator = uuid4_string_generator()
    for _ in range(10):
        response = ResponseBatch(
            uid=next(uid_generator),
            inpits=np.array([1, 2, 3, 4]),
            parameters={},
            model=stateful_model,
            status=Status.CREATED,
            outputs=[np.array([1, 2, 3, 4])],
            pictures=[np.array([1, 2, 3, 4])]
        )
        sock_sender.send_pyobj(response)
    print('Start listenning')


if __name__ == '__main__':
    main()
