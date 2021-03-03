"""
This module is responsible for save mappings into LevelDB
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import time

import plyvel  # type: ignore

import src.data_models as dm


def save_mapping(config: dm.Config, mapping: dm.BatchMapping):
    """
    Save mapping in LevelDB

    Parameters
    ----------
    config:
        Config object, required field is db_address
    mapping:
        BatchMapping object, that will be saved
    """
    while True:
        try:
            database = plyvel.DB(
                config.db_file, create_if_missing=config.create_db_file
            )
            break
        except plyvel._plyvel.IOError:
            time.sleep(config.send_batch_timeout)
            continue
    database.put(*mapping.to_key_value())

    database.close()
