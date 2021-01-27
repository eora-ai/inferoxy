import sys

sys.path.append("..")

import data_models as dm  # type: ignore
from runner import Runner

zmq_config = dm.ZMQConfig(
    zmq_sndhwm=10,
    zmq_rcvhwm=10,
    zmq_sndtimeo=3600000,
    zmq_rcvtimeo=3600000,
)

dataset_address = "tcp://*:5556"
results_address = "tcp://*:5546"
dataset_sync_address = "tcp://*:5555"
results_sync_address = "tcp://*:5545"
batch_size = 1

runner = Runner(
    dataset_address=dataset_address,
    results_address=results_address,
    dataset_sync_address=dataset_sync_address,
    results_sync_address=results_sync_address,
    batch_size=batch_size,
    config=zmq_config,
)

if __name__ == "__main__":
    runner.start()
