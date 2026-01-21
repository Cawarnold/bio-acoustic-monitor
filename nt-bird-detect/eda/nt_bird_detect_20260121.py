#nt_bird_detect_20251211.py

#-------- Import packages --------#
import os
import glob

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

#import pyarrow.parquet as pq # https://arrow.apache.org/docs/python/parquet.html #error on install

import sys

## conda env
### nt_bird_webapp_conda_env_20260116


# ==========================================
# 1. DIRECTORY CONFIGURATION
# ==========================================

### 1. Project Root Discovery
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # dir of this file
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../")) # root dir of project

### 2. Base Data Directories
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")
ANALYTICS_DATA_DIR = os.path.join(PROJECT_ROOT, "data/analytics")


# for each monitor we will go in and loop through the recordings 
# then process each recording to get data
# then if successful add the filename to a parquet file for easier access later
# then 



# 1. SETUP PATHS
# Adjust these to your local paths as needed
recordings_directory_path =  os.path.join(PROJECT_ROOT, "data/raw/wrangcombe_audio1/Data") 
parquet_file_path = os.path.join(PROJECT_ROOT, "data/processed/wrangcombe_audio1/recordings_batch_20260121.parquet") 

# Initialize the BirdNET-Analyzer.
analyzer = Analyzer()

# Get list of files in directory
entries = sorted(os.listdir(recordings_directory_path))

# 3. PROCESSING LOOP
error_files = []
all_new_detections = [] # List to hold DataFrames from each audio file
counter_files = 0

print(f"Starting analysis of {len(entries)} entries...")

for file in entries:
    if not file.lower().endswith('.wav'): continue # skip non-wav files
    
    counter_files += 1
    directory_path_file = os.path.join(recordings_directory_path, file)
    
    # Extract metadata from filename
    # Assuming format: Prefix_YYYYMMDD_HHMMSS.wav
    file_date = file[9:17]
    file_time = file[18:24]
    file_year = int(file[9:13])
    file_month = int(file[13:15])
    file_day = int(file[15:17])

    print(f"Analyzing file number {counter_files}: {file}")

    # Set up the BirdNET recording object
    recording = Recording(
        analyzer,
        directory_path_file,
        lat=50.9481,
        lon=-3.2503,
        date=datetime(year=file_year, month=file_month, day=file_day),
        min_conf=0.5,
    )
    
    try:
        recording.analyze()
        
        # Convert this specific file's detections to a DataFrame
        df_single_file = pd.DataFrame(recording.detections)
        
        # Add metadata columns
        df_single_file['file_name'] = file
        df_single_file['file_date'] = file_date
        df_single_file['file_time'] = file_time
        
        # Store in our list instead of writing to disk yet
        all_new_detections.append(df_single_file)
        
    except Exception as e:
        error_files.append(file) # append errored file name to error list
        print(f"Error analyzing file {file}: {e}")
        continue

# 4. FINAL CONSOLIDATION AND SAVE
if all_new_detections:
    print("\nConsolidating all detections...")
    
    # Combine all individual DataFrames into one
    df_recordings_results = pd.concat(all_new_detections, ignore_index=True)

    # Check if a Parquet file already exists to merge with existing data
    if os.path.exists(parquet_file_path):
        print("Merging with existing Parquet data...")
        df_stored_recordings = pd.read_parquet(parquet_file_path)
        df_combined = pd.concat([df_stored_recordings, df_recordings_results], ignore_index=True)
    else:
        df_combined = df_recordings_results

    # Save once at the very end
    try:
        df_combined.to_parquet(parquet_file_path, index=False)
        print(f"--- SUCCESS ---")
        print(f"Total detections saved: {len(df_combined)}")
        print(f"New detections added this run: {len(df_recordings_results)}")
    except Exception as e:
        print(f"Error saving Parquet: {e}")
else:
    print("No new detections were processed.")

if error_files:
    print(f"Warning: The following files failed analysis: {error_files}")