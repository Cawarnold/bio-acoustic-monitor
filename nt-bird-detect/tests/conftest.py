import os
import pytest

MONITOR_NAME = "wrangcombe_audio1"
home_dir = os.path.expanduser('~')
PROCESSED_DATA_DIR = os.path.join(home_dir, 'Developer/Projects_NotesData/NT(bio-acoustic-monitor)/data/processed')

@pytest.fixture(scope="session")
def monitor_name():
    return MONITOR_NAME

@pytest.fixture(scope="session")
def processed_data_dir():
    return PROCESSED_DATA_DIR
