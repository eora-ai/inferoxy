"""Tests for src.builder module"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import numpy as np

import src.data_models as dm
from src.builder import build_batch


def test_batch_build_empty():
    """Test for zero case"""
    assert build_batch([]) == []


def string_generator():
    for i in range(10):
        yield str(i)


def test_batch_build_one():
    """Test build for one request object"""
    model = dm.ModelObject(
        "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
    )
    request_object = dm.RequestObject(
        "test", np.array([1, 2, 3, 4]), "internal_123123", parameters={}, model=model
    )

    expected_batch = dm.BatchObject(
        next(string_generator()), [np.array([1, 2, 3, 4])], [{}], model=model
    )

    result = build_batch([request_object], uid_generator=string_generator())
    assert result == [(expected_batch, [request_object])]


def test_batch_stateless_many():
    """
    Test build for many stateless request objects
    """
    model1 = dm.ModelObject(
        "stub", "registry.visionhub.ru/models/stub:v3", stateless=True, batch_size=128
    )
    model2 = dm.ModelObject(
        "blur", "registry.visionhub.ru/models/blur:v3", stateless=True, batch_size=128
    )
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=model1,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=model2,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={},
        model=model1,
    )

    batch_uid_generator = string_generator()

    expected_value = [
        (
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs, request_object3.inputs],
                parameters=[request_object1.parameters, request_object3.parameters],
                model=model1,
            ),
            [request_object1, request_object3],
        ),
        (
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object2.inputs],
                parameters=[request_object2.parameters],
                model=model2,
            ),
            [request_object2],
        ),
    ]
    result_value = build_batch(
        [request_object1, request_object2, request_object3],
        uid_generator=string_generator(),
    )
    assert result_value == expected_value


def test_batch_statefull_many():
    """
    Test build for many statefull request objects
    """
    model1 = dm.ModelObject(
        "stub", "registry.visionhub.ru/models/stub:v3", stateless=False, batch_size=128
    )
    model2 = dm.ModelObject(
        "blur", "registry.visionhub.ru/models/blur:v3", stateless=False, batch_size=128
    )
    uid_generator = string_generator()
    request_object1 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=model1,
    )
    request_object2 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_124",
        parameters={},
        model=model2,
    )
    request_object3 = dm.RequestObject(
        uid=next(uid_generator),
        inputs=np.array(range(10)),
        source_id="internal_123_123",
        parameters={"gif_id": 12},
        model=model1,
    )

    batch_uid_generator = string_generator()

    expected_value = [
        (
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object1.inputs, request_object3.inputs],
                parameters=[request_object1.parameters, request_object3.parameters],
                model=model1,
            ),
            [request_object1, request_object3],
        ),
        (
            dm.BatchObject(
                uid=next(batch_uid_generator),
                inputs=[request_object2.inputs],
                parameters=[request_object2.parameters],
                model=model2,
            ),
            [request_object2],
        ),
    ]
    result_value = build_batch(
        [request_object1, request_object2, request_object3],
        uid_generator=string_generator(),
    )
    assert result_value == expected_value
