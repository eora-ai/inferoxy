from pydantic import BaseModel, Field
from typing import Union

from shared_modules.parse_config import recursive_update_all_values, get_nested_key


def test_get_nested_key():
    d = {
        "a": 1,
        "b": {
            "c": 3,
            "d": 4,
        },
    }

    assert get_nested_key(d, ["a"]) == 1
    assert get_nested_key(d, ["b", "c"]) == 3
    assert get_nested_key(d, ["b", "d"]) == 4
    assert get_nested_key(d, ["b", "e"], 5) == 5


def test_recursive_update_all_values():
    class SampleConfigModel(BaseModel):
        test: str
        timeout: float

    values = {"test": "hello"}
    result = recursive_update_all_values(
        SampleConfigModel, values, ["sample"], value_storage={"SAMPLE_TIMEOUT": 3}
    )
    assert result == {"test": "hello", "timeout": 3}


def test_recursive_update_all_values_nested_structure():
    class AnotherNestedConfig(BaseModel):
        address: str
        foo: float

    class NestedConfig(BaseModel):
        max_retries: int
        another_nested_config: AnotherNestedConfig

    class SampleConfigModel(BaseModel):
        test: str
        nested_config: NestedConfig
        timeout: float

    values = {
        "test": "hello",
        "nested_config": {
            "max_retries": 12,
            "another_nested_config": {"address": "google.com", "foo": 123},
        },
    }
    result = recursive_update_all_values(
        SampleConfigModel,
        values,
        ["sample"],
        value_storage={"SAMPLE_TIMEOUT": 3, "SAMPLE_NESTED_CONFIG_MAX_RETRIES": 44},
    )
    assert result == {
        "test": "hello",
        "timeout": 3,
        "nested_config": {
            "max_retries": 44,
            "another_nested_config": {"address": "google.com", "foo": 123},
        },
    }


def test_recursive_update_all_values_branching_structure():
    class FirstBranch(BaseModel):
        max_retries: int

    class SecondBranch(BaseModel):
        address: str
        keep_alive: float

    class SampleConfigModel(BaseModel):
        test: str
        branching: Union[FirstBranch, SecondBranch] = Field(
            required=True, choose_function=lambda x: x["branch_name"] == "SecondBranch"
        )
        timeout: float

    values = {"test": "hello", "branching": {"keep_alive": 12}}
    result = recursive_update_all_values(
        SampleConfigModel,
        values,
        ["sample"],
        value_storage={
            "SAMPLE_TIMEOUT": 3,
            "SAMPLE_SECOND_BRANCH_ADDRESS": "google.com",
        },
    )
    assert result == {
        "test": "hello",
        "timeout": 3,
        "branching": {"address": "google.com", "keep_alive": 12},
    }
