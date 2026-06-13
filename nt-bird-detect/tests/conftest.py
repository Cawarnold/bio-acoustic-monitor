import os
import pytest

MONITOR_NAME = "wrangcombe_audio1"
PROCESSED_DATA_DIR = '/Volumes/Extreme SSD/NatureThriveData/data/processed'

@pytest.fixture(scope="session")
def monitor_name():
    return MONITOR_NAME

@pytest.fixture(scope="session")
def processed_data_dir():
    return PROCESSED_DATA_DIR
