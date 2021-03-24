"""
Connector to remote vision-hub database
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"
import json
from typing import Iterable

import yaml

import src.data_models as dm  # type: ignore
from src.database import Database  # type: ignore
import src.exceptions as exc  # type: ignore
from src.schemas import Model  # type: ignore


class Connector:
    def __init__(self, database: Database):
        """
        Initialize connector
        """
        self.database = database

    def load_models(self):
        with open("/etc/inferoxy/models.yaml") as config_file:
            models_dict = yaml.full_load(config_file)
        models = []
        for key, value in models_dict.items():
            self.save_to_db(key, json.dumps(value))
            data = {"name": key, **value}
            models.append(self.build_model_object(data))
        return models

    def save_models(self, models: Iterable[Model]):
        for model in models:
            self.save_model(model)

    def save_model(self, model: Model):
        key = model.name
        model_dict = model.dict()
        try:
            key = model_dict.pop("name", None)
        except KeyError:
            raise exc.ValidationError("`name` field is required")
        self.save_to_db(key, json.dumps(model_dict))

    def update_model(self, model_slug: str, model_params: dict):
        model_dict = self.fetch_model(model_slug)
        model_dict.update(model_params)

        # Remove `name` from model dict to save in database
        slug = model_dict.pop("name", None)

        self.save_to_db(slug, json.dumps(model_dict))

        # Put `name` in model_dict
        model_dict["name"] = slug

        return model_dict

    def fetch_model_obj(self, model_slug: str) -> dm.ModelObject:
        data = self.fetch_model(model_slug)
        model_obj = self.build_model_object(data)
        return model_obj

    def fetch_model(self, model_slug: str) -> dict:
        data = json.loads(self.database.get(model_slug))  # type: ignore
        data["name"] = model_slug
        return data

    def delete_model(self, model_slug: str):
        self.database.delete(model_slug)

    def save_to_db(self, key, value):
        self.database.set(key, value)

    @staticmethod
    def build_model_object(model_params):
        model = dm.ModelObject(
            name=model_params["name"],
            address=model_params["address"],
            batch_size=model_params["batch_size"],
            run_on_gpu=model_params["run_on_gpu"],
            stateless=model_params["stateless"],
        )
        return model
