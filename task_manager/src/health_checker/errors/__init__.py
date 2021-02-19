"""
"""

from .base_error import HealthCheckError, FatalError, RetriableError


class ContainerDoesNotExists(RetriableError):
    """
    Retraible error, may occure when spot instance disable
    """

    code = "W001"


class ContainerExited(FatalError):
    """
    May occure when there are bug in the model
    """

    code = "E001"


class ConnectionIdleTimeout(FatalError):
    """
    May occure if connection is broken between model and Inferoxy
    """

    code = "E011"


class PodDoesNotExists(RetriableError):
    """
    Retraible error, may occure when spot instance disable
    """

    code = "W002"


class PodExited(FatalError):
    """
    May occure when there are bug in the model
    """

    code = "E002"
