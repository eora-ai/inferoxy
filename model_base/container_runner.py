import sys
import argparse
from pathlib import Path

from shared_modules.parse_config import read_config_with_env
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
        "--result_addr",
        help="Address to open socket for result queue",
        default="tcp://*:5555",
    )
    parser.add_argument(
        "--test_mode", type=str, default="0", help="Whether to run in test mode"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1, help="Batch size to run model"
    )
    args = parser.parse_args()

    config = read_config_with_env(dm.ZMQConfig, "/model_base/config.yaml", "")

    if args.test_mode != "1":
        runner = Runner(
            dataset_address=args.dataset_addr,
            results_address=args.result_addr,
            batch_size=args.batch_size,
            config=config,
        )
        runner.start()
    else:
        test_images_dir = Path(__file__).resolve().parent.parent / "app/test_data"
        tester = Tester(test_images_dir, args.batch_size)
        tester.run_tests()
    sys.stdout.flush()
