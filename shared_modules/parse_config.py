import yaml
from loguru import logger
from pydantic import BaseModel


def build_new_path(config_path: str):
    config, ext = config_path.split(".")
    config += "_env"
    result = config + "." + ext
    return result


def build_config_file(config: BaseModel, config_path: str, manager: str):
    env_prefix = manager.upper()
    dfs("", config, env_prefix)
    env_config = config.dict()
    env_config_path = build_new_path(config_path)

    logger.info(f"Config file with env variables {env_config_path}")

    with open(env_config_path, "w") as file:
        yaml.dump(env_config, file)

    return env_config_path


def dfs(key, item, env_var):
    if isinstance(item, BaseModel):
        for child_key, child_value in item:
            child_env_var = env_var + "_" + child_key.upper()

            if child_value == "$":
                new_value = "${" + child_env_var + "}"

                logger.debug(f"Add env variable \t {new_value}")

                setattr(item, child_key, new_value)

            if not isinstance(child_value, BaseModel) and child_value != "$":
                new_value = "$" + child_env_var + "| " + str(child_value)

                logger.debug(f"Add env variable \t {new_value}")

                setattr(item, child_key, new_value)

            dfs(child_key, child_value, child_env_var)
