"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from dataclasses import dataclass
from typing import List, Optional


from src.utils.data_transfers.sender import Sender
from src.utils.data_transfers.receiver import Receiver

from shared_modules.data_objects import (
    ModelObject,
    MinimalBatchObject,
    Status,
    ResponseBatch,
    ZMQConfig,
    PortConfig,
)


@dataclass
class RunningMeanConfig:
    """
    Config for `RunningMeanStatelessChecker`
    """

    min_threshold: float
    max_threshold: float
    window_size: int


@dataclass
class TriggerPipelineConfig:
    """
    Config for `src.load_analyzer.triggers.TriggerPipeline`
    """

    max_model_percent: float


@dataclass
class LoadAnalyzerConfig:
    """
    Configuration for load analyzer
    """

    sleep_time: float
    trigger_pipeline: TriggerPipelineConfig
    running_mean: RunningMeanConfig


@dataclass
class Config:
    """
    Config of task manager
    """

    zmq_output_address: str
    zmq_input_address: str
    docker_registry: str
    docker_login: str
    docker_password: str
    gpu_all: List[int]
    load_analyzer: LoadAnalyzerConfig

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        """
        Convert dict into Config object
        """
        load_analyzer_dict = config_dict.pop("load_analyzer")
        running_mean_dict = load_analyzer_dict.pop("running_mean")
        trigger_pipeline_dict = load_analyzer_dict.pop("trigger_pipeline")
        running_mean = RunningMeanConfig(**running_mean_dict)
        trigger_pipeline = TriggerPipelineConfig(**trigger_pipeline_dict)
        load_analyzer = LoadAnalyzerConfig(
            running_mean=running_mean,
            trigger_pipeline=trigger_pipeline,
            **load_analyzer_dict
        )
        return cls(load_analyzer=load_analyzer, **config_dict)


@dataclass
class ModelInstance:
    """
    Store connection to the model
    """

    model: ModelObject
    source_id: Optional[str]
    sender: Sender
    receiver: Receiver
    lock: bool
    container_name: str
    running: bool
    num_gpu: Optional[int] = None


RequestBatch = MinimalBatchObject
