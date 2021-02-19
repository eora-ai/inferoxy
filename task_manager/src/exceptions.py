"""
Base execptions for task manager
"""
from loguru import logger

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


class TagDoesNotExists(Exception):
    pass


class CloudClientErrors(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(message)


class ImageNotFound(CloudClientErrors):
    """
    Rise when docker image not found
    """

    def __init__(self, message="Image not found"):
        super().__init__(message)


class ContainerNotFound(CloudClientErrors):
    """
    Rise when running docker container not found
    """

    def __init__(self, message="Container not found"):
        super().__init__(message)


class CloudAPIError(CloudClientErrors):
    """
    Rise when error from cloud
    """

    def __init__(self, message="Cloud error"):
        super().__init__(message)
