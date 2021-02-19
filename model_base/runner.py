import sys
import importlib

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
        batch_size,
        config,
    ):
        """
        Initialize Model class which iterates from datasets samples given by host server and send results of
        processing those samples.

        :param dataset_address: address of socket to connect to receive from dataset sender (zmq format)
        :param results_address: address of socket to bind to send result (zmq format)
        """
        self.batch_size = batch_size
        self.receiver = Receiver(
            open_address=dataset_address,
            config=config,
        )
        self.sender = Sender(
            open_address=results_address,
            config=config,
        )
        self._prepare_model()
        logger.info("Runner inited")

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
        while True:
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
        logger.debug(f"Batch recived {minimal_batch}")
        if minimal_batch is None:
            logger.warning("Batch object is None\n")

        for request_info in minimal_batch.requests_info:
            sample = dict()
            if "sound" in request_info.parameters:
                sample["sound"] = request_info.parameters.get("sound")
            if "init" in request_info.parameters:
                sample["init"] = request_info.parameters.get("init")
                self.init(**sample["init"])
            sample["image"] = request_info.input
            samples.append(sample)

            # samples is a list of dict of dicts having structure:
            # - image: np.ndarray of shape (H, W, 3) and dtype=np.uint8,
            # order of channels - RGB
            # - sound: np.ndarray of shape (2,)(for stereo) or
            # (1,)(for mono) and dtype=np.uint8
            # - meta: serializable dict with keys required by model

        # List of dictionaries prediciton and image
        results = self.predict_batch(samples, draw=True)

        response_batch = self.build_response_batch(minimal_batch, results)

        return response_batch

    @staticmethod
    def build_response_batch(minimal_batch, results):
        """
        Build Response Batch object from Minimal Batch Object
        """
        responses_info = []

        for i, item in enumerate(results):
            prediction = item["prediction"]
            image = item["image"]
            parameters = minimal_batch.requests_info[i].parameters

            if "sound" in results[i]:
                parameters["sound"] = results[i]["sound"]
            response_info = dm.ResponseInfo(
                output=prediction,
                picture=image,
                parameters=parameters,
            )
            responses_info.append(response_info)

        response_batch = dm.ResponseBatch.from_minimal_batch_object(
            batch=minimal_batch, responses_info=responses_info
        )
        return response_batch
