import sys
import math
import json
import pickle
import logging
import traceback
import importlib

import cv2  # type: ignore
import numpy as np  # type: ignore
from PIL import Image  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_results(results, print_prediction=False):
    n_res = len(results)
    for j, res in enumerate(results):
        prediction = res["prediction"]
        if print_prediction:
            logger.info(f"prediction {j + 1}/{n_res}: {prediction}")
        # try to serialize
        json.dumps(prediction)

        image = res["image"]
        assert (
            (type(image) is np.ndarray)
            and (image.ndim == 3)
            and (image.shape[2] == 3)
            and (image.dtype == np.uint8)
        ), "Image must be a numpy.ndarray of shape (height, width, 3) and be of type np.uint8"


class SamplesReader:
    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError


class ImgReader(SamplesReader):
    def __init__(self, dirpath):
        assert (
            dirpath.exists() and dirpath.is_dir()
        ), "Path to test samples must exist and must be a directory"
        self.samples_paths = list(dirpath.iterdir())
        self.n_samples = len(self.samples_paths)
        assert (
            self.n_samples > 0
        ), "There must be at least one sample in the images folder"
        self.item = 0

    def __next__(self):
        if self.item >= self.n_samples:
            raise StopIteration()

        path = self.samples_paths[self.item]
        sample = self._read_sample(path)
        self.item += 1

        return [sample], path

    def __len__(self):
        return self.n_samples

    @staticmethod
    def _read_sample(path):
        if (
            path.match("*.jpeg")
            or path.match("*.JPEG")
            or path.match("*.jpg")
            or path.match("*.JPG")
            or path.match("*.png")
            or path.match("*.PNG")
        ):
            img = Image.open(str(path))
            sample = {"image": np.array(img)}

        if path.match("*.pickle") or path.match("*.pkl"):
            with open(str(path), "rb") as f:
                sample = pickle.load(f)

        return sample


class VideoReader(SamplesReader):
    def __init__(self, video_path, batch_size):
        self.batch_size = batch_size
        self.cap = cv2.VideoCapture(str(video_path))
        n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.n_batches = math.ceil(n_frames / batch_size) if batch_size > 0 else 1
        self.item = 0

    def get_init_params(self):
        height, width = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        init_params = {"height": height, "width": width, "fps": fps, "length": length}

        return init_params

    def __next__(self):
        if self.item >= self.n_batches:
            self.cap.release()
            raise StopIteration()

        samples = []
        i = 0
        while i < self.batch_size or self.batch_size == 0:
            ok, frame = self.cap.read()
            if not ok:
                self.cap.release()
                break

            sample = {"image": frame[..., ::-1]}
            samples.append(sample)
            i += 1

        self.item += 1

        return samples

    def __len__(self):
        return self.n_batches


class Tester:
    predict_batch = None

    def __init__(self, test_data_dir, batch_size):
        self.test_data_dir = test_data_dir
        self.batch_size = batch_size

        logger.info("Setting up tester...")
        self._prepare_model()
        logger.info("Tester is ready.")

    def _prepare_model(self):
        sys.path.append("/app")
        model = importlib.import_module("model")
        self.predict_batch = model.predict_batch
        if "init" in dir(model):
            self.init = model.init
        else:
            self.init = None

    def _process_images(self, samples_reader, mode):
        n_failed = 0
        logger.info(f"[{mode}] Testing started.")
        n_samples = len(samples_reader)

        for i, (sample, path) in enumerate(samples_reader):
            logger.info(f"[{i + 1}/{n_samples} sample]: {str(path)}")

            try:
                results = self.predict_batch(sample, draw=True)
                check_results(results, print_prediction=True)
            except Exception:
                logger.error(f"[{i + 1}/{n_samples} sample]: FAILED!")
                n_failed += 1
                traceback.print_exc()
            else:
                logger.info(f"[{i + 1}/{n_samples} sample]: PASSED.")

        logger.info("=" * 20)
        if n_failed > 0:
            logger.error(
                f"[{mode}] {n_samples - n_failed}/{n_samples} sample. TEST FAILED!"
            )
        else:
            logger.info(
                f"[{mode}] {n_samples - n_failed}/{n_samples} sample. TEST PASSED."
            )
        logger.info("=" * 20)

    def _process_videos(self, videos_dir, mode):
        n_failed = 0
        logger.info(f"[{mode}] Testing started.")

        assert (
            videos_dir.exists() and videos_dir.is_dir()
        ), "Path to test videos must exist and must be a directory"
        videos_paths = list(videos_dir.iterdir())
        videos_paths = list(
            filter(
                lambda path: path.match("*.mp4") or path.match("*.avi"), videos_paths
            )
        )

        n_videos = len(videos_paths)

        for i, video_path in enumerate(videos_paths):
            video_reader = VideoReader(video_path, self.batch_size)

            logger.info(f"[{i + 1}/{n_videos} video] {str(video_path)}")

            init_params = video_reader.get_init_params()
            if self.init:
                self.init(**init_params)

            n_samples = len(video_reader)
            try:
                for j, samples in enumerate(video_reader):
                    logger.info(f"[{j + 1}/{n_samples} batch]")
                    results = self.predict_batch(samples, draw=True)
                    check_results(results)
            except Exception:
                logger.error(f"[{i + 1}/{n_videos} video]: FAILED!")
                n_failed += 1
                traceback.print_exc()
            else:
                logger.info(f"[{i + 1}/{n_videos} video]: PASSED.")

        logger.info("=" * 20)
        if n_failed > 0:
            logger.error(
                f"[{mode}] {n_videos - n_failed}/{n_videos} video. TEST FAILED!"
            )
        else:
            logger.info(
                f"[{mode}] {n_videos - n_failed}/{n_videos} video. TEST PASSED."
            )
        logger.info("=" * 20)

    def run_tests(self):
        img_dir = self.test_data_dir / "images"
        if img_dir.exists():
            img_reader = ImgReader(img_dir)
            self._process_images(img_reader, "IMAGE_MODE")

        videos_dir = self.test_data_dir / "videos"
        if videos_dir.exists():
            self._process_videos(videos_dir, "VIDEO_MODE")
