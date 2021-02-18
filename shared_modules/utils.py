"""Uitls functions for batch manager"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import uuid
import random
import string
from typing import Generator


def uuid4_string_generator() -> Generator[str, None, None]:
    """
    Make from uuid4 generator of random strings

    Returns
    -------
    Generator[str]
        Infinite random strings generator
    """
    while True:
        uid = uuid.uuid4()
        yield str(uid)


def id_generator(
    self, size=6, chars=string.ascii_lowercase
) -> Generator[str, None, None]:
    """
    Generate random string in lowercase
    """
    while True:
        random_string = "".join(random.choice(chars) for _ in range(size))
        yield str(random_string)
