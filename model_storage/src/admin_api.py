"""
CRUD admin API for model storage
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import os
import time

from fastapi import FastAPI, Depends, HTTPException
from uvicorn.config import logger

import src.data_models as dm  # type: ignore
import src.exceptions as exc  # type: ignore
from src.schemas import Model  # type: ignore
from src.database import Redis  # type: ignore
from src.connector import Connector  # type: ignore

app = FastAPI()


def get_connection():
    config_db = dm.DatabaseConfig(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", 6379),
    )
    database = Redis(config_db)
    connector = Connector(database)
    yield connector


@app.get("/models/{model_slug}", response_model=Model)
def get_model(model_slug: str, connector: Connector = Depends(get_connection)):
    """
    Get model object via model slug
    """
    try:
        model_dict = connector.fetch_model(model_slug)

    except exc.SlugDoesNotExist as ex:
        raise HTTPException(status_code=404, detail=ex.message)

    except exc.CannotConnectToDatabase as ex:
        raise HTTPException(status_code=500, detail=ex.message)
    return model_dict


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
