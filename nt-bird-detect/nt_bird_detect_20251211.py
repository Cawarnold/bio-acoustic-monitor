#nt_bird_detect_20251211.py
# Import packages
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


## Directories
wave_file_2025 = '/Users/christianarnold/Documents/MyProjects/NatureThrive/20250907_Recordings/Data/S4A27301_20250818_141329.wav'

recordings_directory_path = '/Users/christianarnold/Documents/MyProjects/NatureThrive/20251122_Recordings/Data' #154 files
#recordings_directory_path = '/Users/christianarnold/Documents/MyProjects/NatureThrive/20250907_Recordings/Data' #176 files
#recordings_directory_path = '/Users/christianarnold/Documents/MyProjects/NatureThrive/20251209_trials_5_recordings/Data' # 5 files
parquet_directory_path = '/Users/christianarnold/Documents/MyProjects/NatureThrive/recordings_parquet/recordings_20251210.parquet'


## Get list of files in directory
entries = os.listdir(recordings_directory_path)

for file in entries:
    directory_path_file = os.path.join(recordings_directory_path, file)
    file_date = file[9:17]
    file_time = file[18:24]
    file_year = int(file[9:13])
    file_month = int(file[13:15])
    file_day = int(file[15:17])
    print(f"Analyzing file: {file}")
    print(f"Date: {file_date}, Time: {file_time}, Year: {file_year}, Month: {file_month}, Day: {file_day}")
