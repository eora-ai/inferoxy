""" Test set sound of results in runner"""
__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import sys

import numpy as np  # type: ignore

sys.path.append("..")

import model_base.data_models as dm  # type: ignore
from model_base.runner import Runner


zmq_config = dm.ZMQConfig(
    zmq_sndhwm=10,
    zmq_rcvhwm=10,
    zmq_sndtimeo=3600000,
    zmq_rcvtimeo=3600000,
)

dataset_address = "tcp://*:5556"
results_address = "tcp://*:5546"
dataset_sync_address = "tcp://*:5555"
results_sync_address = "tcp://*:5545"
batch_size = 1


results = [  # type: ignore
    {
        "prediction": [],
        "image": [],
        "sound": [],
    }
]

request_info = dm.RequestInfo(input=[], parameters={})
model_object = dm.ModelObject(
    name="stub",
    address="",
    stateless=True,
    batch_size=1,
)
minimal_batch = dm.MinimalBatchObject(
    uid="test",
    requests_info=[request_info],
    model=model_object,
)


def test_change_from_results():
    response_info = dm.ResponseInfo(output=[], parameters={"sound": []}, picture=[])

    expected_result = dm.ResponseBatch(
        uid="test",
        requests_info=[request_info],
        model=model_object,
        responses_info=[response_info],
    )

    response_batch = Runner.build_response_batch(minimal_batch, results)

    assert np.array_equal(
        expected_result.responses_info[0].parameters["sound"],
        response_batch.responses_info[0].parameters["sound"],
    )


results = [
    {
        "prediction": [],
        "image": [],
    }
]

request_info = dm.RequestInfo(input=[], parameters={"sound": []})
model_object = dm.ModelObject(
    name="stub",
    address="",
    stateless=True,
    batch_size=1,
)
minimal_batch = dm.MinimalBatchObject(
    uid="test",
    requests_info=[request_info],
    model=model_object,
)


def test__sound_from_params():
    response_info = dm.ResponseInfo(output=[], parameters={"sound": []}, picture=[])

    expected_result = dm.ResponseBatch(
        uid="test",
        requests_info=[request_info],
        model=model_object,
        responses_info=[response_info],
    )
    response_batch = Runner.build_response_batch(minimal_batch, results)

    assert np.array_equal(
        expected_result.responses_info[0].parameters["sound"],
        response_batch.responses_info[0].parameters["sound"],
    )


results = [
    {
        "prediction": [],
        "image": [],
    },
    {
        "prediction": [],
        "image": [],
        "sound": np.array([1, 255]),
    },
]
request_info1 = dm.RequestInfo(input=[], parameters={"sound": []})
request_info2 = dm.RequestInfo(input=[], parameters={})

model_object = dm.ModelObject(
    name="stub",
    address="",
    stateless=True,
    batch_size=1,
)
minimal_batch = dm.MinimalBatchObject(
    uid="test",
    requests_info=[request_info1, request_info2],
    model=model_object,
)


def test_mixed():
    response_info1 = dm.ResponseInfo(output=[], parameters={"sound": []}, picture=[])
    response_info2 = dm.ResponseInfo(
        output=[], parameters={"sound": np.array([1, 255])}, picture=[]
    )

    expected_result = dm.ResponseBatch(
        uid="test",
        requests_info=[request_info1, request_info2],
        model=model_object,
        responses_info=[response_info1, response_info2],
    )
    response_batch = Runner.build_response_batch(minimal_batch, results)
    assert np.array_equal(
        expected_result.responses_info[0].parameters["sound"],
        response_batch.responses_info[0].parameters["sound"],
    )
    assert np.array_equal(
        expected_result.responses_info[1].parameters["sound"],
        response_batch.responses_info[1].parameters["sound"],
    )
