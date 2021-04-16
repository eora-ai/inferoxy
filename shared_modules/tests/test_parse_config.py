from pydantic import BaseModel

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
    class NestedConfig(BaseModel):
        max_retries: int

    class SampleConfigModel(BaseModel):
        test: str
        timeout: float
        nested_config: NestedConfig

    values = {"test": "hello", "nested_config": {"max_retries": 12}}
    result = recursive_update_all_values(
        SampleConfigModel,
        values,
        ["sample"],
        value_storage={"SAMPLE_TIMEOUT": 3, "SAMPLE_NESTED_CONFIG_MAX_RETRIES": 44},
    )
    assert result == {
        "test": "hello",
        "timeout": 3,
        "nested_config": {"max_retries": 44},
    }
