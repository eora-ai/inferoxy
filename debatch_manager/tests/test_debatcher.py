"""
Tests for src.debather module
"""

import numpy as np
import src.data_models as dm
from shared_modules.data_objects import (
    ResponseBatch,
    Status,
    BatchMapping)

from src.debatcher import (
    debatch
)


stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)
response_batch = ResponseBatch(
    uid='test',
    inputs=np.array([1, 2, 3, 4]),
    model=stub_model,
    status=Status.CREATED,
    outputs=[np.array([1, 2, 3, 4])],
    pictures=[np.array([1, 2, 3, 4])]
)

batch_mapping = BatchMapping(
        batch_uid="test1",
        request_object_uids=['robj1'],
        source_ids=['robjsource1'],
    )


def test_debatch():
    result = debatch(response_batch, batch_mapping)
    assert result[0].uid == 'robj1'


if __name__ == '__main__':
    test_debatch()
