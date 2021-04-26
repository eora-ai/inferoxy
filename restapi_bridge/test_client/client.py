import requests
import numpy as np
from PIL import Image

url = "http://localhost:8698/infer"

image = np.asarray(Image.open("test.jpg"))
shape = list(image.shape)

payload = {
    "source_id": "test.jpg",
    "model": "stub",
    "inputs": [
        {
            "parameters": {},
            "data": image.reshape((1, -1)).tolist(),
            "shape": shape,
            "datatype": "uint8",
        }
    ],
}


print(payload)

response = requests.post(url, json=payload)
print(response.json())
