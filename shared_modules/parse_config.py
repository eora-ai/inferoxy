import os
from dataclasses import fields, is_dataclass

from loguru import logger
from pydantic_yaml import YamlModel
from pydantic import BaseModel

import src.data_models as dm


def replace_env(config: YamlModel, manager: str):
    env_prefix = manager.upper()
    dfs("", config, env_prefix)
    return config


def dfs(key, item, env_var):
    if isinstance(item, dict):
        for child_key, child_value in item.items():
            child_env_var = env_var + "_" + child_key.upper()
            if child_value is None:
                logger.debug(f"Change env variable {child_env_var}")
                item[child_key] = os.environ.get(child_env_var)

            dfs(child_key, child_value, child_env_var)

    elif is_dataclass(item):
        print("Enter dataclass")
        for field in fields(item):
            value = getattr(item, field.name)
            child_env_var = env_var + "_" + str(field.name).upper()

            if value is None:
                new_value = os.environ.get(child_env_var)
                logger.debug(f"Change env variable {child_env_var}")
                setattr(item, field.name, new_value)

            dfs(field.name, value, child_env_var)

    elif isinstance(item, BaseModel):
        print("Enter in pydantic")
        for child_key, child_value in item:
            child_env_var = env_var + "_" + child_key.upper()

            if child_value is None:
                logger.debug(f"Change env variable {child_env_var}")
                new_value = os.environ.get(child_env_var)
                setattr(item, child_key, new_value)

            dfs(child_key, child_value, child_env_var)
