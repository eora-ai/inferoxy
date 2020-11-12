"""
This module is responsible for save mappings into LevelDB
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import plyvel

import src.data_models as dm


def create_db(config: dm.Config) -> plyvel.DB:
    """
    Create connection to LevelDB

    Parameters
    ----------
    config:
        Config object, required field is db_address
    """
    return plyvel.DB(config["db_file"], create_if_missing=config["create_db_file"])


def save_mapping(database: plyvel.DB, mapping: dm.BatchMapping):
    """
    Save mapping in LevelDB

    Parameters
    ----------
    database:
        LevelDB DB instance
    mapping:
        BatchMapping object, that will be saved
    """
    database.put(mapping.to_key_value())
