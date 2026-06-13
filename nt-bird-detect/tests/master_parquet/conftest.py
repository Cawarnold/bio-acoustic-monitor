import os
import pytest
import pandas as pd

@pytest.fixture(scope="session")
def df_master(processed_data_dir, monitor_name):
    path = os.path.join(processed_data_dir, monitor_name, "recordings_MASTER.parquet")
    return pd.read_parquet(path)
