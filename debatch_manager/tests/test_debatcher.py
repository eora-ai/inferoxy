"""
Tests for src.debather module
"""

import numpy as np  # type: ignore
from shared_modules.data_objects import (
    ResponseBatch,
    Status,
    BatchMapping,
    ModelObject,
)

from src.debatcher import (
    debatch,
)


stub_model = ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)
response_batch = ResponseBatch(
    uid='test',
    inputs=np.array([1, 2, 3, 4]),
    parameters=[{'sest': 'test'}],
    model=stub_model,
    status=Status.CREATED,
    outputs=[np.array([1, 2, 3, 4]),
             np.array([5, 6, 7, 8]),
             np.array([9, 10])],
    pictures=[np.array([1, 2, 3, 4]), np.array([5, 6, 7, 8]), np.array([])]
)

batch_mapping = BatchMapping(
        batch_uid="test",
        request_object_uids=['robj1', 'test', 'roobj-3'],
        source_ids=['robjsource1', 'test', 'robjsource-3'],
    )


def test_debatch_many():
    result = debatch(response_batch, batch_mapping)
    assert result[0].uid == 'robj1'
    assert result[0].source_id == 'robjsource1'

    assert result[1].uid == 'test'
    assert result[1].source_id == 'test'

    assert result[2].uid == 'roobj-3'
    assert result[2].output[0].get('output').size == np.array([9, 10]).size
    assert result[2].output[0].get('output')[0] == 9
    assert result[2].output[0].get('output')[1] == 10


response_batch_one = ResponseBatch(
    uid='test',
    inputs=np.array([1, 2, 3, 4]),
    parameters=[{'sest': 'test'}],
    model=stub_model,
    status=Status.CREATED,
    outputs=[np.array([1, 2, 3, 4])],
    pictures=[np.array([1, 2, 3, 4])]
)

batch_mapping_one = BatchMapping(
        batch_uid="test",
        request_object_uids=['robj1'],
        source_ids=['robjsource1']
    )


def test_debatch_one():
    result = debatch(response_batch, batch_mapping)
    assert result[0].uid == 'robj1'
    assert result[0].source_id == 'robjsource1'

    assert result[0].output[0].get('output')[0] == 1
    assert result[0].output[0].get('output')[1] == 2
    assert result[0].output[0].get('output')[2] == 3
    assert result[0].output[0].get('output')[3] == 4

    assert result[0].output[0].get('picture')[0] == 1
    assert result[0].output[0].get('picture')[1] == 2
    assert result[0].output[0].get('picture')[2] == 3
    assert result[0].output[0].get('picture')[3] == 4


response_batch_empty = ResponseBatch(
    uid='test',
    inputs=[],
    parameters=[],
    model=stub_model,
    status=Status.CREATED,
    outputs=[],
    pictures=[]
)

batch_mapping_empty = BatchMapping(
        batch_uid="test",
        request_object_uids=[],
        source_ids=[],
    )


def test_debatch_empty():
    result = debatch(response_batch_empty, batch_mapping_empty)
    len(result) == 0
