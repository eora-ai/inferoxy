"""
Utils that will help to make parameterized configs using yaml and env
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import re
from pathlib import Path
from typing import Type, List, Any, Optional

import yaml
from loguru import logger
from pydantic import BaseModel


def build_new_path(path: Path, suffix: str = "env") -> Path:
    """
    Build new path from existing path by adding suffix

    Parameters
    ----------
    path:
        some input path
    suffix:
        Suffix that will be add to name

    Returns
    -------
        new path object with `suffix`

    Examples
    --------
    >>> build_new_path(Path("config.yaml"), suffix="env")
    PosixPath('config_env.yaml')

    >>> build_new_path(Path("/etc/inferoxy/config.yaml"))
    PosixPath('/etc/inferoxy/config_env.yaml')
    """
    ext = path.suffix
    config_name = path.stem
    config_name += "_" + suffix
    return Path(path.parent / (config_name + ext))


def add_env_variables_to_config(
    config_values: dict,
    config_type: Type[BaseModel],
    config_path: Path,
    env_prefix: str,
):
    env_prefix = env_prefix.upper()
    env_config_path = build_new_path(config_path)

    config_with_env = recursive_update_all_values(
        config_type, config_values, [env_prefix]
    )

    logger.info(f"Config file with env variables {env_config_path}")

    with open(env_config_path, "w") as yaml_file:
        yaml.dump(config_with_env, yaml_file)

    return env_config_path


def recursive_update_all_values(
    config_type: Type[BaseModel],
    config_values: dict,
    name_prefixes: List[str],
    index_prefixes: Optional[list] = None,
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

    Returns
    -------
        Dict with all names needed to make config file and
        values equal to coresponding env variable name
    """

    if index_prefixes is None:
        index_prefixes = []

    result_dict = {}
    for name, model_field in config_type.__fields__.items():
        if not issubclass(model_field.type_, BaseModel):
            value = get_nested_key(config_values, index_prefixes + [name], None)
            new_value = make_env_value(name_prefixes, name, optional_value=value)
            set_nested_key(result_dict, index_prefixes, name, new_value)
        else:
            snake_name = camel_to_snake_case(name)
            result_dict.update(
                recursive_update_all_values(
                    model_field.type_,
                    config_values,
                    name_prefixes + [snake_name],
                    index_prefixes=index_prefixes + [snake_name.lower()],
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


def set_nested_key(d: dict, keys: list, key: Any, value: Any):
    """
    Set value in nested dictionary
    """
    new_d = d
    for k in keys:
        if not k in new_d:
            new_d[k] = {}
        if isinstance(new_d[k], dict):
            new_d = new_d[k]
        else:
            raise ValueError()
    new_d[key] = value


def make_env_value(prefixes: List[str], key: str, optional_value=None) -> str:
    """
    Convert prefxise and key into env variable name

    Examples
    --------
    >>> make_env_value(["sample", "test"], "timeout", optional_value=3)
    $SAMPLE_TEST_TIMEOUT|3
    >>> make_env_value([], "timeout", optional_value=3)
    $TIMEOUT|3
    """
    name = "_".join(map(str.upper, prefixes + [key]))
    if not optional_value is None:
        name += f"|{str(optional_value)}"
    return "$" + name


def camel_to_snake_case(inp: str) -> str:
    """
    Transforms camel case into snake case
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", inp)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
