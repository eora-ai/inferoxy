"""Uitls functions for batch manager"""

__author__ = "Andrey Chertkov"
__email__ = "a.chertkov@eora.ru"

import uuid

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
