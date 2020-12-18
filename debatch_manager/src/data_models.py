"""
Data object definitions
"""

from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration of batch_manager

    Parameters
    ----------
    zmq_input_address:
        Address of zreomq socket ipc for input requests
    zmq_output_address:
        Address of zreomq socket ipc for result batches
    db_file:
        File path to leveldb
    """

    zmq_input_address: str
    zmq_output_address: str
    db_file: str
