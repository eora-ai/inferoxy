import os
from dataclasses import fields, is_dataclass

from loguru import logger
from pydantic import BaseModel

import src.data_models as dm    # type: ignore


def build_config(path: str, manager: str):
    config = dm.Config.parse_file(path, content_type="yaml")
    env_prefix = manager.upper()
    dfs("", config, env_prefix)
    return config


def dfs(key, item, env_var):
    if isinstance(item, dict):
        for child_key, child_value in item.items():
            child_env_var = env_var + "_" + child_key.upper()
            if child_value is None:
                new_value = os.environ.get(child_env_var)

                logger.debug(f"Change env variable {child_env_var}\
                             to {new_value}")

                item[child_key] = new_value

            dfs(child_key, child_value, child_env_var)

    elif is_dataclass(item):
        annotations = item.__anotations__
        print("Enter dataclass")
        for field in fields(item):
            value = getattr(item, field.name)
            child_env_var = env_var + "_" + str(field.name).upper()

            if value is None:
                type_value = annotations.get(field.name)

                env_val = os.environ.get(child_env_var)
                if env_val is None:
                    # oshibka
                    pass

                try:
                    converted_value = type_value(env_val)
                except ValueError:
                    # Failed to convert
                    pass

                logger.debug(f"Change env variable {child_env_var}\
                             to {new_value}")

                setattr(item, field.name, converted_value)

            dfs(field.name, value, child_env_var)

    elif isinstance(item, BaseModel):
        print("Enter in pydantic")
        for child_key, child_value in item:
            child_env_var = env_var + "_" + child_key.upper()

            if child_value is None:
                new_value = os.environ.get(child_env_var)

                logger.debug(f"Change env variable {child_env_var}\
                             to {new_value}")

                setattr(item, child_key, new_value)

            dfs(child_key, child_value, child_env_var)
