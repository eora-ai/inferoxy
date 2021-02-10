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
        self.connection = psycopg2.connect(
            user=self.config.user,
            host=self.config.host,
            password=self.config.password,
            port=self.config.port,
        )

    def fetch_model(self, model_slug: str):
        try:
            logger.info("Connecting to the PostgreSQL database...")
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

            sql_query = f"""SELECT
            slug,
            name,
            link,
            batch_size,
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
            name=model_params["name"],
            address=model_params["link"],
            batch_size=model_params["batch_size"],
            # TODO replace field
            stateless=any([s in [1, 3] for s in model_params["supported_modes"]]),
        )
        return model
