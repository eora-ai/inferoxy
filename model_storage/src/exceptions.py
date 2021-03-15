"""
Base exceptions for model storage
"""
from loguru import logger

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"


class AdminAPIError(Exception):
    def __init__(self, message):
        self.message = message


class SlugDoesNotExist(AdminAPIError):
    pass


class CannotSaveModel(AdminAPIError):
    pass


class CannotConnectToDatabase(AdminAPIError):
    pass


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
