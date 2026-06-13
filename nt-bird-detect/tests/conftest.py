import os
import sys

import pytest

# Add src to path so tests share the same pipeline config as the scripts
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
from config import PROCESSED_DATA_DIR, monitor_name as MONITOR_NAME


@pytest.fixture(scope="session")
def monitor_name():
    return MONITOR_NAME


@pytest.fixture(scope="session")
def processed_data_dir():
    return PROCESSED_DATA_DIR
