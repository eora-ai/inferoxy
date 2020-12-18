"""
Check that LevelDB contains batches
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import sys

import plyvel
import yaml
import src.data_models as dm

sys.path.append("..")


def main():

    with open("../config.yaml") as f:
        config_dict = yaml.full_load(f)
        config = dm.Config(**config_dict)
    db = plyvel.DB(config.db_file)

    for (key, value) in db:
        print(f"{key=}, {value=}")


if __name__ == "__main__":
    main()
