"""
Test client for debatcher manager
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys
import zmq  # type: ignore
import yaml
import plyvel  # type: ignore
import numpy as np  # type: ignore

sys.path.append("..")

import src.data_models as dm
from shared_modules.data_objects import (
    ModelObject,
    ResponseBatch,
    BatchMapping,
    Status,
)
from shared_modules.utils import uuid4_string_generator


stateful_model = ModelObject(
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

    # Create sockets
    sock_sender = ctx.socket(zmq.PUB)
    sock_sender.connect(config.zmq_input_address)
    sock_receiver = ctx.socket(zmq.SUB)
    sock_receiver.bind(config.zmq_output_address)
    sock_receiver.subscribe(b"")

    try:
        db = plyvel.DB(config.db_file, create_if_missing=True)
    except IOError:
        raise RuntimeError("Failed to open database")

    uid_generator = uuid4_string_generator()

    responses = []

    for _ in range(10):
        # Generate uid for batch mapping and batch response
        uid = next(uid_generator)

        # Create batch mapping
        batch_mapping = BatchMapping(
            batch_uid=uid,
            request_object_uids=["request-test-1", "request-test-2"],
            source_ids=["source-id-test-1", "source-id-test-2"],
        )

        # Create response batch and add to list of response batches
        request_info1 = dm.RequestInfo(
            input=np.array([1, 2, 3, 4]),
            parameters={},
        )
        request_info2 = dm.RequestInfo(
            input=np.array([5, 6, 7, 8]),
            parameters={},
        )
        response_info1 = dm.ResponseInfo(
            output=np.array([1, 2, 3, 4]),
            picture=np.array([5, 6, 7, 8]),
            parameters={},
        )
        response_info2 = dm.ResponseInfo(
            output=np.array([1, 2, 3, 4]),
            picture=np.array([5, 6, 7, 8]),
            parameters={},
        )
        responses += [
            ResponseBatch(
                uid=uid,
                requests_info=[request_info1, request_info2],
                model=stateful_model,
                status=Status.CREATED,
                responses_info=[response_info1, response_info2],
            )
        ]

        # Put in database
        db.put(*batch_mapping.to_key_value())

    # Close connection
    db.close()

    # Send response batches to debatch manager
    for response in responses:
        sock_sender.send_pyobj(response)

    # Receive response objects from debatch manager
    while True:
        response_object = sock_receiver.recv_pyobj()
        print(response_object)


if __name__ == "__main__":
    main()
