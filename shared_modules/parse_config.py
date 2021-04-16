"""
Utils that will help to make parameterized configs using yaml and env
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import os
import re
from pathlib import Path
from typing import Type, List, Any, Optional

import yaml
from loguru import logger
from pydantic import BaseModel


def populate_config_with_env_values(
    config_type: Type[BaseModel],
    config_path: Path,
    env_prefix: str,
) -> BaseModel:
    """
    Read config from a file and populate values using environment variables

    Parameters
    ----------
    config_type:
        Type of the config
    config_path:
        Path to the config file
    env_prefix:
        Prefix that will be appended to the env variables names,
        usually name of the manager
    """
    logger.info(f"Read config for {env_prefix} from {config_path}")
    with open(config_path, "r") as file_:
        config_dict = yaml.full_load(file_)
    new_config_dict = recursive_update_all_values(
        config_type, config_dict, [env_prefix]
    )
    return config_type(new_config_dict)


def recursive_update_all_values(
    config_type: Type[BaseModel],
    config_values: dict,
    name_prefixes: List[str],
    index_prefixes: Optional[list] = None,
    value_storage=None,
) -> dict:
    """
    Recursive iterate over nested pydantic model structure
    and set values to "$PREFIX_FIELD_NAME|value" format.
    This is needed for envyaml on unmarshal read values from environment

    Parameters
    ----------
    config_type:
        Is needed to getting structure of the config
    config_values:
        Values that was read from .yaml files
    name_prefixes:
        This is needed to save nested structure in env variable name
    index_prefixes:
        Needed to call `get_nested_key` and `set_nested_key`
    value_storage:
        Something that have `get(key, default=None)` method

    Returns
    -------
        Dict with all names needed to make config file and
        values equal to coresponding env variable name
    """

    if index_prefixes is None:
        index_prefixes = []
    if value_storage is None:
        value_storage = os.environ

    result_dict = {}
    for name, model_field in config_type.__fields__.items():
        if not issubclass(model_field.type_, BaseModel):
            value = get_nested_key(config_values, index_prefixes + [name], None)
            env_name = make_env_name(name_prefixes, name)
            new_value = value_storage.get(env_name, value)
            set_nested_key(result_dict, index_prefixes, name, new_value)
        else:
            snake_name = camel_to_snake_case(name)
            result_dict.update(
                recursive_update_all_values(
                    model_field.type_,
                    config_values,
                    name_prefixes + [snake_name],
                    index_prefixes=index_prefixes + [snake_name.lower()],
                    value_storage=value_storage,
                )
            )

    return result_dict


def get_nested_key(dict_: dict, keys: list, default=None) -> Any:
    """
    Return value from the nested dict

    Parameters
    ----------
    dict_:
        Nested dict
    keys:
        List of keys, using as a path to value
    default:
        Default value, that will be returned if some key from `keys` are not in the dict

    Returns
    -------
        Return value from nested dict

    Examples
    --------
    >>> get_nested_key({ "a": 1, "b": { "c": 3, "d": 4, }, }, ["a"]) == 1
    True

    >>> get_nested_key({ "a": 1, "b": { "c": 3, "d": 4, }, }, ["b", "c"]) == 3
    True

    >>> get_nested_key({ "a": 1, "b": { "c": 3, "d": 4, }, }, ["b", "d"]) == 4
    True

    >>> get_nested_key({ "a": 1, "b": { "c": 3, "d": 4, }, }, ["b", "e"], 5) == 5
    True
    """
    new_dict = dict_
    for k in keys:
        if isinstance(new_dict.get(k, default), dict):
            new_dict = new_dict.get(k, default)
        else:
            return new_dict.get(k, default)
    return new_dict


def set_nested_key(dict_: dict, keys: list, key: Any, value: Any):
    """
    Set value in nested dictionary
    """
    new_dict = dict_
    for k in keys:
        if not k in new_dict:
            new_dict[k] = {}
        if isinstance(new_dict[k], dict):
            new_dict = new_dict[k]
        else:
            raise ValueError()
    new_dict[key] = value


def make_env_name(prefixes: List[str], key: str) -> str:
    """
    Convert prefxise and key into env variable name

    Examples
    --------
    >>> make_env_value(["sample", "test"], "timeout")
    SAMPLE_TEST_TIMEOUT
    >>> make_env_value([], "timeout")
    TIMEOUT
    """
    name = "_".join(map(str.upper, prefixes + [key]))
    return name


def camel_to_snake_case(inp: str) -> str:
    """
    Transforms camel case into snake case
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", inp)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
