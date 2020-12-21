"""
Test client for debatcher manager
"""
import sys
import uuid
from typing import Generator

import zmq
import yaml
import plyvel
import numpy as np

sys.path.append("..")

import src.data_models as dm
from shared_modules.data_objects import (
    ModelObject,
    ResponseBatch,
    BatchMapping,
    Status,
)


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
    print('Create socket...')
    sock_sender = ctx.socket(zmq.PUB)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.SUB)
    print('Binding socket...')
    sock_receiver.bind(config.zmq_output_address)

    sock_receiver.subscribe(b"")

    # try:
    db = plyvel.DB(config.db_file, create_if_missing=True)
#    except IOError:
#        raise RuntimeError('Failed to open database')
#
    uid_generator = uuid4_string_generator()
    responses = []
    for _ in range(10):
        uid = next(uid_generator)
        batch_mapping = BatchMapping(
            batch_uid=uid,
            request_object_uids=['request-test-1'],
            source_ids=['source-id-test-1']
        )
        print(f'Create batch mapping batch uid = {uid}')
        responses += [ResponseBatch(
            uid=uid,
            inputs=np.array([1, 2, 3, 4]),
            parameters={},
            model=stateful_model,
            status=Status.CREATED,
            outputs=[np.array([1, 2, 3, 4])],
            pictures=[np.array([1, 2, 3, 4])],
        )]
        db.put(*batch_mapping.to_key_value())
    db.close()
    for response in responses:
        sock_sender.send_pyobj(response)


if __name__ == "__main__":
    main()
