"""
Pydantic models for admin API
"""

__author__ = "Madina Gafarova"
__email__ = "m.gafarova@eora.ru"

from pydantic import BaseModel


class Model(BaseModel):
    name: str
    address: str
    stateless: bool
    batch_size: int
    run_on_gpu: bool
