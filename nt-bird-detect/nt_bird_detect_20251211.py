#nt_bird_detect_20251211.py

######### Import packages #########
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


######### Main code #########

## Directories
home_dir = os.path.expanduser('~')
#recordings_directory_path = os.path.join(home_dir, 'Documents/MyProjects/NatureThrive', '20251122_Recordings/Data') #154 files
#recordings_directory_path = os.path.join(home_dir, 'Documents/MyProjects/NatureThrive', '20250907_Recordings/Data') #176 files
recordings_directory_path = os.path.join(home_dir, 'Documents/MyProjects/NatureThrive', '20251209_trials_5_recordings/Data') # 5 files
parquet_file_path = os.path.join(home_dir, 'Documents/MyProjects/NatureThrive', 'recordings_parquet/recordings_20251212.parquet') # parquet file

## Get list of files in directory
entries = sorted(os.listdir(recordings_directory_path))

# Initialize the BirdNET-Analyzer.
analyzer = Analyzer()

error_files = []
counter_files = 0
for file in entries:
    counter_files += 1
    if not file.lower().endswith('.wav'): continue # skip non-wav files
    directory_path_file = os.path.join(recordings_directory_path, file)
    print(f"Analyzing file number {counter_files}: {file}")
    file_date = file[9:17]
    file_time = file[18:24]
    file_year = int(file[9:13])
    file_month = int(file[13:15])
    file_day = int(file[15:17])
    print(f"Date: {file_date}, Time: {file_time}, Year: {file_year}, Month: {file_month}, Day: {file_day}")

    recording = Recording(
        analyzer,
        directory_path_file,
        lat=50.9481,
        lon=-3.2503,
        date=datetime(year=file_year, month=file_month, day=file_day),  # use date or week_48
        min_conf=0.01,
    )
    
    print(f"Analyzing file: {file}")
    try:
        recording.analyze()
    except Exception as e:
        error_files.append(file) # append errored file name to error list
        print(f"Error analyzing file {file}: {e}")
        continue

    #print("Load data into DataFrame")
    df_recordings_results = pd.DataFrame(recording.detections)

    # Add file name and date columns to DataFrame
    df_recordings_results['file_name'] = file
    df_recordings_results['file_date'] = file_date
    df_recordings_results['file_time'] = file_time

    #print("If Parquet file exists, read it and concatenate, else use current DataFrame")
    if os.path.exists(parquet_file_path):
        df_stored_recordings = pd.read_parquet(parquet_file_path)
        #print("Combine both DataFrames")
        df_combined = pd.concat([df_stored_recordings, df_recordings_results], ignore_index=True)
        df = df_combined
    else:
        df = df_recordings_results

    # Save the DataFrame to a Parquet file
    # index=False tells Pandas NOT to save the row indices (0, 1, 2...) as a column
    #print("Save combined DataFrame back to Parquet")
    try:
        df.to_parquet(parquet_file_path, index=False)
    except ImportError:
        print("Error: Failed to save DataFrame to Parquet")


    #print(directory_path_file)
    #print(file_date, file_time, file_year, file_month, file_day)