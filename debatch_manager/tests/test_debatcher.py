"""
Tests for src.debather module
"""

import numpy as np
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
    outputs=[np.array([1, 2, 3, 4])],
    pictures=[np.array([1, 2, 3, 4])]
)

batch_mapping = BatchMapping(
        batch_uid="test",
        request_object_uids=['robj1'],
        source_ids=['robjsource1', 'test'],
    )


def test_debatch():
    result = debatch(response_batch, batch_mapping)
    assert result[0].uid == 'robj1'
    assert result[0].source_id == 'robjsource1'
