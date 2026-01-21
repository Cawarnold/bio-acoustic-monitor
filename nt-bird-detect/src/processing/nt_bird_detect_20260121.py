#nt_bird_detect_20251211.py

#-------- Import packages --------#
import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

#import pyarrow.parquet as pq # https://arrow.apache.org/docs/python/parquet.html #error on install

import sys


#-------- Main code --------#

## Directories
### 1. Project Root Discovery
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # dir of this file
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../")) # root dir of project

### 2. Base Data Directories
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")
ANALYTICS_DATA_DIR = os.path.join(PROJECT_ROOT, "data/analytics")

### 3. Dynamic Monitor Handling
#### Instead of hardcoding 'wrangcombe_audio1', we list all folders in 'raw'
monitors = [f for f in os.listdir(RAW_DATA_DIR) if os.path.isdir(os.path.join(RAW_DATA_DIR, f))]

recordings_path = os.path.join(RAW_DATA_DIR, monitors[0], 'Data')
print(recordings_path)
