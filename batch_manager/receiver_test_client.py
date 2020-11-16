"""
This is test receiver for batch manager
"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"


import yaml
import zmq

import src.data_models as dm


def main():
    with open("config.yaml") as f:
        config_dict = yaml.full_load(f)
        config = dm.Config(**config_dict)

    ctx = zmq.Context()
    sock_receiver = ctx.socket(zmq.SUB)
    sock_receiver.bind(config.zmq_output_address)
    sock_receiver.subscribe(b"")
    print("Start listenning")
    while True:
        result = sock_receiver.recv_pyobj()
        print(f"Result batch {result}")


if __name__ == "__main__":
    main()
