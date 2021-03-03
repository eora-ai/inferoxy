"""
Connector to remote vision-hub database
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

import psycopg2
import psycopg2.extras
from loguru import logger

import src.data_models as dm


class Connector:
    def __init__(self, config: dm.DatabaseConfig):
        if config is None:
            logger.error("No database config")
        self.config = config

    def fetch_model(self, model_slug: str):
        try:
            logger.info("Connecting to the PostgreSQL database...")
            self.connection = psycopg2.connect(
                user=self.config.user,
                host=self.config.host,
                password=self.config.password,
                port=self.config.port,
                dbname=self.config.dbname,
            )
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

            sql_query = f"""SELECT
            slug,
            link,
            batch_size,
            gpu,
            supported_modes  FROM  models_model WHERE slug='{model_slug}'"""
            cursor.execute(sql_query)

            model_params = cursor.fetchone()

            model = self.build_model_object(model_params)

            return model

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            if self.connection is not None:
                self.connection.close()
                logger.info("Database connection closed")

    @staticmethod
    def build_model_object(model_params):
        model = dm.ModelObject(
            name=model_params["slug"],
            address=model_params["link"],
            batch_size=model_params["batch_size"],
            run_on_gpu=model_params["gpu"],
            # TODO replace field
            stateless=any([s in [1, 3] for s in model_params["supported_modes"]]),
        )
        return model
