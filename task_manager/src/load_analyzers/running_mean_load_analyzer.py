"""
This module is responsible for analyze load using running mean algo
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from src.load_analyzers import BaseLoadAnalyzer
from src.load_analyzers.checkers import (
    StatefulChecker,
    RunningMeanStatelessChecker,
    EnoughResourcesChecker,
)


class RunningMeanLoadAnalyzer(BaseLoadAnalyzer):
    """
    Load analyzer based on running mean of request per model
    """

    checkers = [EnoughResourcesChecker, StatefulChecker, RunningMeanStatelessChecker]
