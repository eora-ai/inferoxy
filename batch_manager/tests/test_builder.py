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
        next(string_generator()), [np.array([1, 2, 3, 4])], {}, model=model
    )

    result = build_batch([request_object], string_generator())
    assert result == [(expected_batch, [request_object])]
