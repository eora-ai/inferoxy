import importlib
import sys
import yaml  # type: ignore

from loguru import logger

import data_models as dm  # type: ignore
from data_transfer import Sender, Receiver  # type: ignore


class Runner:
    predict_batch = None
    init = None

    def __init__(
        self,
        dataset_address,
        results_address,
        dataset_sync_address,
        results_sync_address,
        batch_size,
    ):
        """
        Initialize Model class which iterates from datasets samples given by host server and send results of
        processing those samples.

        :param dataset_address: address of socket to connect to receive from dataset sender (zmq format)
        :param results_address: address of socket to bind to send result (zmq format)
        """
        with open("/model_base/config.yaml") as config_file:
            config_dict = yaml.full_load(config_file)
            config = dm.ZMQConfig(**config_dict)

        self.batch_size = batch_size
        self.receiver = Receiver(
            open_address=dataset_address,
            sync_address=dataset_sync_address,
            config=config,
        )
        self.sender = Sender(
            open_address=results_address,
            sync_address=results_sync_address,
            config=config,
        )
        self._prepare_model()

    def _prepare_model(self):
        """
        Imports necessary functions from model's module
        :return: None
        """
        sys.path.append("/app")
        model = importlib.import_module("model")
        self.predict_batch = model.predict_batch
        if "init" in dir(model):
            self.init = model.init

    def start(self):
        """
        Runs model predictions in a loop until empty message is being sent
        :return: None
        """
        # 1. Get sample from input queue
        # 2. Run model on sample
        # 3. Send result back
        response_batch = self._process_next_batch()
        self.sender.send(response_batch)

        self.receiver.close()
        self.sender.close()

    def _process_next_batch(self):
        """
        Processes newly received messages chunking them by batch size elements
        :return: list of dicts dicts having structure:
        - prediction: serializable dict with model output data
        - image: result of drawing - np.ndarray of shape (H, W, 3) and dtype=np.uint8, order of channels - RGB
        """
        # supported modes:
        # - img2img (batch_size = 1)
        # - vid2vid (1 <= batch_size <= N)
        # - img2vid (batch_size = 1)
        # - vid2img (batch_size = 0)
        samples = []

        minimal_batch = self.receiver.receive()
        if minimal_batch is None:
            logger.warning("Sample is None\n")

        for input_image in minimal_batch.inputs:
            sample = dict()
            sample["image"] = input_image
            samples.append(sample)

            # samples is a list of dict of dicts having structure:
            # - image: np.ndarray of shape (H, W, 3) and dtype=np.uint8,
            # order of channels - RGB
            # - sound: np.ndarray of shape (2,)(for stereo) or
            # (1,)(for mono) and dtype=np.uint8
            # - meta: serializable dict with keys required by model

            # List of dictionaries prediciton and image
            results = self.predict_batch(samples, draw=True)
            # self.__set_sound_for_results_if_needed(results, samples)

        response_batch = self.build_response_batch(minimal_batch, results)

        return response_batch

    def build_response_batch(self, minimal_batch, meta):
        """
        Build Response Batch object from Minimal Batch Object
        """
        outputs = []

        for item in meta:
            prediction = item["prediction"]
            image = item["image"]
            outputs.append([{"output": prediction, "picture": image}])

        response_batch = dm.ResponseBatch.from_minimal_batch_object(
            batch=minimal_batch, outputs=outputs
        )
        return response_batch

    @staticmethod
    def __set_sound_for_results_if_needed(results, samples):
        for i in range(len(results)):
            if "sound" in results[i]:
                return
            if "sound" not in samples[i]:
                return
            results[i]["sound"] = samples[i]["sound"]
