import argparse
import sys
import yaml
from pathlib import Path

import data_models as dm  # type: ignore
from runner import Runner  # type: ignore
from tester import Tester  # type: ignore


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Container runner: works in two modes: \n"
        "1) waits for messages from data sender "
        "and runs model for predictions\n"
        "2) traverse test images and runs model for predictions"
    )
    parser.add_argument(
        "--dataset_addr",
        help="Address of socket for dataset queue",
        default="tcp://*:5556",
    )
    parser.add_argument(
        "--dataset_sync_addr",
        help="Address of socket to sync dataset queue",
        default="tcp://*:5546",
    )
    parser.add_argument(
        "--result_addr",
        help="Address to open socket for result queue",
        default="tcp://*:5555",
    )
    parser.add_argument(
        "--result_sync_addr",
        help="Address to open socket for sync result queue",
        default="tcp://*:5545",
    )
    parser.add_argument(
        "--test_mode", type=str, default="0", help="Whether to run in test mode"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1, help="Batch size to run model"
    )
    args = parser.parse_args()

    with open("/model_base/config.yaml") as config_file:
        config_dict = yaml.full_load(config_file)
        config = dm.ZMQConfig(**config_dict)

    if args.test_mode != "1":
        runner = Runner(
            dataset_address=args.dataset_addr,
            results_address=args.result_addr,
            dataset_sync_address=args.dataset_sync_addr,
            results_sync_address=args.result_sync_addr,
            batch_size=args.batch_size,
            config=config,
        )
        runner.start()
    else:
        test_images_dir = Path(__file__).resolve().parent.parent / "app/test_data"
        tester = Tester(test_images_dir, args.batch_size)
        tester.run_tests()
    sys.stdout.flush()
