
__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from abc import ABC, abstractmethod

import redis
from loguru import logger

import src.exceptions as exc    # type: ignore
import src.data_models as dm    # type: ignore


class Database(ABC):
    """
    Interface
    """

    def __init__(self, config: dm.DatabaseConfig):
        """
        Initialize database
        """
        if config is None:
            logger.error("No database config")

    @abstractmethod
    def set(self, key: str, value: str):
        """
        Set value to key
        """

    @abstractmethod
    def delete(self, key: str):
        """
        Delete item
        """

    @abstractmethod
    def get(self, key: str):
        """
        Get item
        """

    @abstractmethod
    def ping(self):
        """
        Check connection
        """


class Redis(Database):
    def __init__(self, config: dm.DatabaseConfig):
        """
        Initialize connector
        """
        if config is None:
            logger.error("No database config")
        self.config = config
        self.redis = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db_num,
        )

    def set(self, key: str, value: str):
        try:
            self.redis.set(key, value)
            self.redis.save()

        except redis.RedisError as ex:
            raise exc.CannotSaveModel(ex.args)
            logger.error("Failed to save model in model storage")

        except redis.exceptions.ConnectionError:
            raise exc.CannotConnectToDatabase(
                "Cannot connect to database"
            )

    def delete(self, key: str):
        try:
            res = self.redis.delete(key)
        except redis.exceptions.ConnectionError:
            raise exc.CannotConnectToDatabase(
                "Cannot connect to database"
            )
        if res == 0:
            raise exc.SlugDoesNotExist(
                "Model with this slug does not exist"
            )

    def get(self, key: str):
        if not self.redis.exists(key):
            raise exc.SlugDoesNotExist(
                "Model with this slug does not exist"
            )
        return self.redis.get(key)

    def ping(self):
        try:
            self.redis.ping()
        except redis.exceptions.ConnectionError:
            raise exc.CannotConnectToDatabase(
                "Cannot connect to database"
            )


class MockRedis(Database):
    def __init__(self):
        self.database = {}

    def set(self, key: str, value: str):
        self.database[key] = value

    def delete(self, key: str):
        if key not in self.database:
            raise exc.SlugDoesNotExist(
                "Model with this slug does not exist"
            )
        self.database.pop(key, None)

    def get(self, key: str):
        if key not in self.database:
            raise exc.SlugDoesNotExist(
                "Model with this slug does not exist"
            )
        res = self.database[key]
        return res

    def ping(self):
        print("PONG")
