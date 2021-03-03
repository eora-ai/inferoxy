"""
Entrypoint of listener component
"""

import yaml
from loguru import logger

from src.adapters.python_zeromq_adapter import ZMQPythonAdapter
import src.data_models as dm


def main():
    with open("config.yaml") as f:
        config_dict = yaml.full_load(f)
        config = dm.Config.from_dict(config_dict)

    adapter = ZMQPythonAdapter(config)
    logger.info("Listener started")
    adapter.start()


if __name__ == "__main__":
    main()
