"""
Tests for src.debather module
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import numpy as np  # type: ignore

import src.data_models as dm
from src.debatcher import (
    debatch,
)


stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)
request_info1 = dm.RequestInfo(
    input=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
request_info2 = dm.RequestInfo(
    input=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
response_info1 = dm.ResponseInfo(
    output=np.array([1, 2, 3, 4]),
    picture=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
response_info2 = dm.ResponseInfo(
    output=np.array([1, 2, 3, 4]),
    picture=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
response_batch = dm.ResponseBatch(
    uid="test",
    model=stub_model,
    requests_info=[request_info1, request_info2],
    status=dm.Status.CREATED,
    mini_batches=[
        dm.MiniResponseBatch([response_info1]),
        dm.MiniResponseBatch([response_info2]),
    ],
)

batch_mapping = dm.BatchMapping(
    batch_uid="test",
    request_object_uids=["robj1", "test"],
    source_ids=["robjsource1", "test"],
)


def test_debatch_many():
    result = debatch(response_batch, batch_mapping)

    assert result[0].uid == "robj1"
    assert result[0].source_id == "robjsource1"

    assert result[1].uid == "test"
    assert result[1].source_id == "test"

    assert result[0].response_info == response_info1
    assert result[1].response_info == response_info2


request_info3 = dm.RequestInfo(
    input=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
response_info3 = dm.ResponseInfo(
    output=np.array([1, 2, 3, 4]),
    picture=np.array([1, 2, 3, 4]),
    parameters={"sest": "test"},
)
response_batch_one = dm.ResponseBatch(
    uid="test",
    model=stub_model,
    requests_info=[request_info3],
    status=dm.Status.CREATED,
    mini_batches=[dm.MiniResponseBatch([response_info3])],
)

batch_mapping_one = dm.BatchMapping(
    batch_uid="test", request_object_uids=["robj1"], source_ids=["robjsource1"]
)


def test_debatch_one():
    result = debatch(response_batch, batch_mapping)
    assert result[0].uid == "robj1"
    assert result[0].source_id == "robjsource1"

    assert result[0].response_info == response_info3


request_info4 = dm.RequestInfo(
    input=np.zeros((1,)),
    parameters={},
)
response_info4 = dm.ResponseInfo(
    output={},
    picture=np.zeros((1,)),
    parameters={},
)
response_batch_empty = dm.ResponseBatch(
    uid="test",
    model=stub_model,
    requests_info=[request_info4],
    status=dm.Status.CREATED,
    mini_batches=[dm.MiniResponseBatch([response_info4])],
)

batch_mapping_empty = dm.BatchMapping(
    batch_uid="test",
    request_object_uids=[],
    source_ids=[],
)


def test_debatch_empty():
    result = debatch(response_batch_empty, batch_mapping_empty)
    len(result) == 0
