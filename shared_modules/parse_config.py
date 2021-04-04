import yaml
from loguru import logger
from pydantic import BaseModel


def build_config(config: BaseModel, config_path: str, manager: str):
    env_prefix = manager.upper()
    dfs("", config, env_prefix)
    env_config = config.dict()
    with open(config_path, "w") as file:
        yaml.dump(env_config, file)


def dfs(key, item, env_var):
    if isinstance(item, BaseModel):
        for child_key, child_value in item:
            child_env_var = env_var + "_" + child_key.upper()

            if child_value == "$":
                new_value = "$" + child_env_var

                logger.debug(f"Change env variable {child_env_var}\
                                to {new_value}")

                setattr(item, child_key, new_value)

            if not isinstance(child_value, BaseModel) and child_value != "$":
                new_value = "$" + child_env_var + "| " + str(child_value)

                logger.debug(f"Change env variable {child_env_var}\
                                to {new_value}")

                setattr(item, child_key, new_value)

            dfs(child_key, child_value, child_env_var)
