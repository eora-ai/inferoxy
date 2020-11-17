"""Tests for src.builder module"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import numpy as np  # type: ignore

import src.data_models as dm
from src.builder import (
    build_batches,
    build_mapping_batch,
    split_on_complete_and_uncomplete_batches,
)


stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
)
small_batch_stub_model = dm.ModelObject(
    "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=2
)
blur_model = dm.ModelObject(
    "blur", "registry.visionhub.ru/models/blur:v3", stateless=True, batch_size=128
)
stub_stateful_model = dm.ModelObject(
    "stub",
    "registry.visionhub.ru/models/stub-stateful:v3",
    stateless=False,
    batch_size=128,
)
blur_stateful_model = dm.ModelObject(
    "blur",
    "registry.visionhub.ru/models/blur-stateful:v3",
    stateless=False,
    batch_size=128,
)


def test_batch_build_empty():
    """Test for zero case"""
    assert build_batches([]) == dm.Batches(batches=[])


def string_generator():
    i = 0
    while True:
        yield str(i)
        i += 1


def test_batch_build_one():
    """Test build for one request object"""
    request_object = dm.RequestObject(
        "test",
        np.array([1, 2, 3, 4]),
        "internal_123123",
        parameters={},
        model=stub_model,
    )

    expected_batch = dm.BatchObject(
        next(string_generator()),
        [np.array([1, 2, 3, 4])],
        [{}],
        model=stub_model,
        request_objects=[request_object],
    )

    result = build_batches([request_object], uid_generator=string_generator())
    assert result == dm.Batches(batches=[expected_batch])


def test_batch_stateless_many():
    """
    Test build for many stateless request objects
    """
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=stub_model,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=blur_model,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=stub_model,
    )

    batch_uid_generator = string_generator()

    expected_value = dm.Batches(
        batches=[
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs, request_object3.inputs],
                parameters=[request_object1.parameters, request_object3.parameters],
                model=stub_model,
                request_objects=[request_object1, request_object3],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object2.inputs],
                parameters=[request_object2.parameters],
                model=blur_model,
                request_objects=[request_object2],
            ),
        ]
    )
    result_value = build_batches(
        [request_object1, request_object2, request_object3],
        uid_generator=string_generator(),
    )
    assert result_value == expected_value


def test_batch_stateful_many():
    """
    Test build for many stateful request objects
    """
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=stub_stateful_model,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_124",
        parameters={},
        model=blur_stateful_model,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=stub_stateful_model,
    )

    batch_uid_generator = string_generator()

    expected_value = dm.Batches(
        batches=[
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs, request_object3.inputs],
                parameters=[request_object1.parameters, request_object3.parameters],
                model=stub_stateful_model,
                request_objects=[request_object1, request_object3],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object2.inputs],
                parameters=[request_object2.parameters],
                model=blur_stateful_model,
                request_objects=[request_object2],
            ),
        ]
    )
    result_value = build_batches(
        [request_object1, request_object2, request_object3],
        uid_generator=string_generator(),
    )
    assert result_value == expected_value


def test_multi_stage_build_batch():
    """
    Test build batch if some batches are provided
    """

    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_124",
        parameters={"gif_id": 12},
        model=stub_model,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=blur_stateful_model,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_125",
        parameters={},
        model=stub_stateful_model,
    )
    request_object4 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_121",
        parameters={},
        model=stub_stateful_model,
    )
    request_object5 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=blur_stateful_model,
    )
    request_object6 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=blur_stateful_model,
    )
    request_object7 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_127",
        parameters={"gif_id": 12},
        model=blur_model,
    )

    batch_uid_generator = string_generator()
    expected_value = dm.Batches(
        batches=[
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs],
                parameters=[request_object1.parameters],
                model=stub_model,
                request_objects=[request_object1],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[
                    request_object2.inputs,
                    request_object5.inputs,
                    request_object6.inputs,
                ],
                parameters=[
                    request_object2.parameters,
                    request_object5.parameters,
                    request_object6.parameters,
                ],
                model=blur_stateful_model,
                request_objects=[request_object2, request_object5, request_object6],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object3.inputs],
                parameters=[request_object3.parameters],
                model=stub_stateful_model,
                request_objects=[request_object3],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object4.inputs],
                parameters=[request_object4.parameters],
                model=stub_stateful_model,
                request_objects=[request_object4],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object7.inputs],
                parameters=[request_object7.parameters],
                model=blur_model,
                request_objects=[request_object7],
            ),
        ]
    )

    build_batch_generator = string_generator()
    result_value = build_batches(
        [request_object1, request_object2, request_object3],
        uid_generator=build_batch_generator,
    )
    result_value = build_batches(
        [request_object4, request_object5, request_object6, request_object7],
        existing_batches=result_value,
        uid_generator=build_batch_generator,
    )
    assert result_value == expected_value


def test_batch_size_limit():
    """
    Test batch size limitation
    """
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=small_batch_stub_model,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=small_batch_stub_model,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=small_batch_stub_model,
    )

    batch_uid_generator = string_generator()

    expected_value = dm.Batches(
        batches=[
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs, request_object2.inputs],
                parameters=[request_object1.parameters, request_object2.parameters],
                model=small_batch_stub_model,
                request_objects=[request_object1, request_object2],
            ),
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object3.inputs],
                parameters=[request_object3.parameters],
                model=small_batch_stub_model,
                request_objects=[request_object3],
            ),
        ]
    )
    result_value = build_batches(
        [request_object1, request_object2, request_object3],
        uid_generator=string_generator(),
    )
    assert result_value == expected_value


def test_build_one_mapping_batch():
    """
    Test for build mapping batch for one case
    """
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=stub_model,
    )
    batches = build_batches([request_object1], uid_generator=string_generator())

    expected_value = dm.BatchMapping(
        batch_uid=next(string_generator()),
        request_object_uids=[request_object1.uid],
        source_ids=[request_object1.source_id],
    )

    assert build_mapping_batch(batches[0]) == expected_value


def test_split_batches():
    """
    Test for split_on_complete_and_uncomplete_batches
    """
    batch1 = dm.BatchObject(
        uid="00",
        inputs=[np.array(range(10)), np.array(range(10))],
        parameters=[{}, {}],
        model=small_batch_stub_model,
        request_objects=[],
    )
    batch2 = dm.BatchObject(
        uid="01",
        inputs=[np.array(range(10))],
        parameters=[{}],
        model=small_batch_stub_model,
        request_objects=[],
    )

    completed, uncompleted = split_on_complete_and_uncomplete_batches(
        dm.Batches([batch1, batch2])
    )
    assert completed.batches[0] == batch1
    assert uncompleted.batches[0] == batch2
