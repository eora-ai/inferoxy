"""
This package is responsible for analyze load, and manage number of running instances
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from .base_load_analyzer import BaseLoadAnalyzer
from .running_mean_load_analyzer import RunningMeanLoadAnalyzer
