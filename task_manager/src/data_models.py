"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from dataclasses import dataclass
from typing import List, Optional, Generic, TypeVar, Union

from pydantic_yaml import YamlModel     # type: ignore

from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from shared_modules.data_objects import (
    ModelObject,
    MinimalBatchObject,
    MiniResponseBatch,
    Status,
    ResponseBatch,
    RequestInfo,
    ResponseInfo,
    ZMQConfig,
    PortConfig,
    BaseConfig,
)


class RunningMeanConfig(BaseConfig):
    """
    Config for `RunningMeanStatelessChecker`
    """

    min_threshold: Union[float, str]
    max_threshold: Union[float, str]
    window_size: Union[int, str]


class TriggerPipelineConfig(BaseConfig):
    """
    Config for `src.load_analyzer.triggers.TriggerPipeline`
    """

    max_model_percent: Union[float, str]


class StatefulChecker(BaseConfig):
    keep_model: Union[int, str]


class LoadAnalyzerConfig(BaseConfig):
    """
    Configuration for load analyzer
    """

    sleep_time: Union[float, str]
    trigger_pipeline: TriggerPipelineConfig
    running_mean: RunningMeanConfig
    stateful_checker: StatefulChecker


class DockerConfig(YamlModel):
    registry: str
    login: str
    password: str
    network: str


class KubeConfig(YamlModel):
    address: str
    token: str
    namespace: str
    create_timeout: Union[int, str]


class ModelsRunnerConfig(BaseConfig):
    ports: PortConfig
    zmq_config: ZMQConfig


class HealthCheckerConfig(BaseConfig):
    """
    Config for health checker
    """

    connection_idle_timeout: Union[int, str] = 10


class Config(YamlModel):
    """
    Config of task manager
    """

    zmq_output_address: str
    zmq_input_address: str
    gpu_all: Union[List[int], str]
    health_check: HealthCheckerConfig
    load_analyzer: LoadAnalyzerConfig
    models: ModelsRunnerConfig
    max_running_instances: Union[int, str] = 10
    docker: Optional[DockerConfig] = None
    kube: Optional[KubeConfig] = None


@dataclass
class ModelInstance:
    """
    Store connection to the model
    """

    model: ModelObject
    source_id: Optional[str]
    sender: BaseSender
    receiver: BaseReceiver
    lock: bool
    hostname: str
    running: bool
    name: str
    num_gpu: Optional[int] = None
    current_processing_batch: Optional[MinimalBatchObject] = None

    def __hash__(self):
        return hash(self.name)


RequestBatch = MinimalBatchObject
T = TypeVar("T")  # pylint: disable=C0103
S = TypeVar("S")  # pylint: disable=C0103


@dataclass
class ReasoningOutput(Generic[T, S]):
    """
    Wrapper for output of any function and adding reason parameters
    For example, `f() -> bool` returns bool,
    we need provide additional information, if result is `False`,
    so we can make `f() -> (bool, Optional[str])`
    in more general case `f() -> (T, Optional[S])`.
    `ReasoningOutput` follows from (T, Optional[S])

    Parameters
    ----------
    output
        Generic value, result of the function
    reason
        String description of the output
    """

    output: T
    reason: Optional[S] = None
