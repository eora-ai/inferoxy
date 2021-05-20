import numpy as np
import sys

from grpc import insecure_channel
from loguru import logger

sys.path.append("../")
from protos.inferenceservice_pb2_grpc import InferenceServiceStub
from protos.inferrequest_pb2 import InferRequest
from protos.inputinferrequest_pb2 import InputInferRequest
from protos.inferdata_pb2 import InferData
from protos.parametermessage_pb2 import ParameterMessage

from PIL import Image

with Image.open("test.jpg") as image_file:
    image = np.asarray(image_file)
    shape = list(image.shape)

with insecure_channel("localhost:5051") as channel:
    response = InferenceServiceStub(channel).Infer(
        InferRequest(
            model="stub",
            source_id="test",
            inputs=[
                InputInferRequest(
                    shape=shape,
                    datatype="uint8",
                    data=InferData(payload_uint=image.ravel().tolist()),
                    parameters={"end": ParameterMessage(bool_param=True)},
                )
            ],
        )
    )
    print(response)
