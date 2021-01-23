"""
Base execptions for task manager
"""
from loguru import logger

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


class TagDoesNotExists(Exception):
    pass


class CloudClientErrors(Exception):
    pass


class ImageNotFound(CloudClientErrors):
    """
    Rise when docker image not found
    """

    def __init__(self, message="Image not found"):
        self.message = message
        logger.error(message)


class ContainerNotFound(CloudClientErrors):
    """
    Rise when running docker container not found
    """

    def __init__(self, message="Container not found"):
        super(ContainerNotFound, self).__init__(message)
        logger.error(message)


class DockerAPIError(CloudClientErrors):
    """
    Rise when unstable internet connection or server error
    """

    def __init__(self, message="Server error"):
        super(DockerAPIError, self).__init__(message)
        logger.error(message)


class CloudAPIError(CloudClientErrors):
    def __init__(self, message="Cloud client API error"):
        super(DockerAPIError, self).__init__(message)
        logger.error(message)
