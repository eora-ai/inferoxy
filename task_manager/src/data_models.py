"""
"""


__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

from dataclasses import dataclass
from typing import List, Optional, Generic, TypeVar

from src.utils.data_transfers.sender import BaseSender
from src.utils.data_transfers.receiver import BaseReceiver
from shared_modules.data_objects import (
    ModelObject,
    MinimalBatchObject,
    Status,
    ResponseBatch,
    RequestInfo,
    ResponseInfo,
    ZMQConfig,
    PortConfig,
    BaseConfig,
)


@dataclass
class RunningMeanConfig(BaseConfig):
    """
    Config for `RunningMeanStatelessChecker`
    """

    min_threshold: float
    max_threshold: float
    window_size: int


@dataclass
class TriggerPipelineConfig(BaseConfig):
    """
    Config for `src.load_analyzer.triggers.TriggerPipeline`
    """

    max_model_percent: float


@dataclass
class StatefulChecker(BaseConfig):
    keep_model: int


@dataclass
class LoadAnalyzerConfig(BaseConfig):
    """
    Configuration for load analyzer
    """

    sleep_time: float
    trigger_pipeline: TriggerPipelineConfig
    running_mean: RunningMeanConfig
    stateful_checker: StatefulChecker


@dataclass
class DockerConfig(BaseConfig):
    registry: str
    login: str
    password: str
    network: str


@dataclass
class KubeConfig(BaseConfig):
    address: str
    token: str
    namespace: str
    create_timeout: int


@dataclass
class ModelsRunnerConfig(BaseConfig):
    ports: PortConfig
    zmq_config: ZMQConfig

    @classmethod
    def from_dict(cls, config_dict: dict) -> "ModelsRunnerConfig":
        ports_config = config_dict["ports"]
        zmq_config = config_dict["zmq_config"]
        return cls(ports=PortConfig(**ports_config), zmq_config=ZMQConfig(**zmq_config))


@dataclass
class HealthCheckerConfig(BaseConfig):
    """
    Config for health checker
    """

    connection_idle_timeout: int = 10


@dataclass
class Config(BaseConfig):
    """
    Config of task manager
    """

    zmq_output_address: str
    zmq_input_address: str
    gpu_all: List[int]
    health_check: HealthCheckerConfig
    load_analyzer: LoadAnalyzerConfig
    models: ModelsRunnerConfig
    max_running_instances: int = 10
    docker: Optional[DockerConfig] = None
    kube: Optional[KubeConfig] = None

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        """
        Convert dict into Config object
        """
        load_analyzer_dict = config_dict.pop("load_analyzer")
        running_mean_dict = load_analyzer_dict.pop("running_mean")
        stateful_checker_dict = load_analyzer_dict.pop("stateful_checker")
        trigger_pipeline_dict = load_analyzer_dict.pop("trigger_pipeline")
        health_check_dict = config_dict.pop("health_check")
        running_mean = RunningMeanConfig(**running_mean_dict)
        trigger_pipeline = TriggerPipelineConfig(**trigger_pipeline_dict)
        stateful_checker = StatefulChecker(**stateful_checker_dict)
        load_analyzer = LoadAnalyzerConfig(
            running_mean=running_mean,
            trigger_pipeline=trigger_pipeline,
            stateful_checker=stateful_checker,
            **load_analyzer_dict
        )
        models_dict = config_dict.pop("models")
        models_config = ModelsRunnerConfig.from_dict(models_dict)
        health_check_config = HealthCheckerConfig(**health_check_dict)
        return cls(
            load_analyzer=load_analyzer,
            models=models_config,
            health_check=health_check_config,
            **config_dict
        )


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
