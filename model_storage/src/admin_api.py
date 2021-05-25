"""
CRUD admin API for model storage
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import time
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from uvicorn.config import logger  # type: ignore

from shared_modules.parse_config import read_config_with_env
from shared_modules.utils import recreate_logger

import src.data_models as dm
import src.exceptions as exc
from src.schemas import Model
from src.database import Redis
from src.connector import Connector

log_level = os.getenv("LOGGING_LEVEL", "INFO")
recreate_logger(log_level, "MODEL_STORAGE_API")

app = FastAPI()


def get_connection():
    config: dm.Config = read_config_with_env(
        dm.Config, "/etc/inferoxy/model_storage.yaml", "model_storage"
    )
    config_db = config.database
    database = Redis(config_db)
    connector = Connector(database)
    yield connector


@app.get("/models/{model_slug}")
def get_model(model_slug: str, connector: Connector = Depends(get_connection)):
    """
    Get model object via model slug
    """
    try:
        model = connector.fetch_model_obj(model_slug)

    except exc.SlugDoesNotExist as ex:
        raise HTTPException(status_code=404, detail=ex.message)

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)
    return model


@app.put("/models")
def update_all_models(
    models: Optional[List[Model]] = None, connector: Connector = Depends(get_connection)
):
    """
    Replace all models using `load_models` + `models`
    """
    try:
        if models is None:
            models = []

        connector.save_models(models)
        models += connector.load_models()
    except exc.CannotSaveModel:
        raise HTTPException(status_code=500, detail="Cannot save model")

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)
    except exc.ValidationError as ex:
        raise HTTPException(status_code=400, detail=ex.message)

    logger.info(f"Inserted models {models}")
    return models


@app.post("/models", response_model=Model)
def create_models(model: Model, connector: Connector = Depends(get_connection)):
    """
    Create model
    """
    try:
        start_time = time.time()
        connector.save_model(model)
        end_time = time.time()
        logger.info(f"save model completed in {end_time - start_time}")
    except exc.CannotSaveModel:
        raise HTTPException(status_code=500, detail="Cannot save model")

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)

    except exc.ValidationError as ex:
        raise HTTPException(status_code=400, detail=ex.message)

    return model


@app.patch("/models/{model_slug}", response_model=Model)
def update_models(
    model_slug: str, model_params: dict, connector: Connector = Depends(get_connection)
):
    """
    Update model fields
    """
    try:
        updated_model = connector.update_model(model_slug, model_params)

    except exc.SlugDoesNotExist as ex:
        raise HTTPException(status_code=404, detail=ex.message)

    except exc.CannotSaveModel as ex:
        raise HTTPException(status_code=500, detail=ex.message)

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)
    return updated_model


@app.delete("/models/{model_slug}")
def delete_model(model_slug: str, connector: Connector = Depends(get_connection)):
    """
    Delete model via model_slug
    """
    try:
        connector.delete_model(model_slug)

    except exc.SlugDoesNotExist as ex:
        raise HTTPException(status_code=404, detail=ex.message)

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)
    return {"model": model_slug}
