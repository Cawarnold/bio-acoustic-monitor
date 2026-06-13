import os
import glob

import pandas as pd
import numpy as np

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

# Central config (src is on sys.path via the calling script / conftest)
from config import monitor_coords

# ==========================================
# parse_sm4_summary() - Parse SM4 Summary Utility
# analyze_audio_file() - Parse Audio File Utility
# get_monitor_coords() - Get Monitor Coordinates Utility
# get_processing_manifest() - Processing Manifest Utilities
# update_manifest() - Processing Manifest Utilities
# consolidate_daily_parquets() - Consolidate Daily Parquets Utility
# ==========================================

# ==========================================
# Parse SM4 Summary Utility
# ==========================================

def parse_sm4_summary(raw_monitor_path, monitor_name):
    """
    Finds all 'DataLoad_YYYYMMDD' folders and extracts metadata.
    In each folder, find the .txt summary file
    and add monitor/file metadata columns,
    then return it as a Pandas DataFrame.
    """
    all_dataframes = []

    # 1. Look for folders starting with 'DataLoad'
    dataload_folders = [f for f in os.listdir(raw_monitor_path) 
                        if os.path.isdir(os.path.join(raw_monitor_path, f)) 
                        and f.startswith('DataLoad')]

    for folder in dataload_folders:
        load_date = folder.replace('DataLoad_', '') # Extract '20260121'
        folder_path = os.path.join(raw_monitor_path, folder)
        
        # 2. Look for the .txt file inside that specific DataLoad folder.
        #    Skip hidden / macOS AppleDouble files (e.g. "._S4A27301_A_Summary.txt")
        #    that the SSD's filesystem creates — they end in .txt but are binary.
        txt_files = [f for f in os.listdir(folder_path)
                     if f.endswith('.txt') and not f.startswith('.')]
        
        for file_name in txt_files:
            txt_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(txt_path, skipinitialspace=True)

            # 3. Add the columns you requested
            df['monitor_name'] = monitor_name
            df['dataload_batch'] = folder      # e.g., DataLoad_20260121
            df['load_date'] = load_date        # e.g., 20260121
            df['source_file'] = file_name
            
            all_dataframes.append(df)
            print(f"Successfully parsed {file_name} from {folder}")

    if not all_dataframes:
        return None
        
    return pd.concat(all_dataframes, ignore_index=True)

# ==========================================
# Parse Audio File Utility
# ==========================================

def analyze_audio_file(analyzer, directory_path_file, lat, lon, date, min_conf):
    """
    Uses BirdNET to analyze a single wav file and returns detections.
    """
    recording = Recording(
        analyzer,
        directory_path_file,
        lat=lat,
        lon=lon,
        date=date,
        min_conf=min_conf,
    )
    
    # We run the analysis and return the result list
    recording.analyze()
    return recording.detections

# ==========================================
# Get Monitor Coordinates Utility
# ==========================================

def _coords_from_row(row):
    """
    Pulls (lat, lon) from a single summary-log row.
    Raises if LAT/LON are missing or not numeric, so the caller can fall back.
    """
    lat, lon = row['LAT'], row['LON']
    if pd.isna(lat) or pd.isna(lon):
        raise ValueError("LAT/LON missing")

    lat, lon = float(lat), float(lon)

    # Adjust longitude if it is marked as West
    if str(row['EW']).strip().lower() == 'w':
        lon = -abs(lon)

    return lat, lon


def get_monitor_coords(processed_dir, monitor_name):
    """
    Returns (lat, lon) for the monitor, in order of preference:
      1. Last row of the summary log  (most recent recorded location)
      2. First row of the summary log (if the last row has no usable coords)
      3. Hardcoded fallback for this monitor from config.monitor_coords
    """
    fallback = monitor_coords.get(monitor_name)
    monitor_summary_log_path = os.path.join(processed_dir, monitor_name, "monitor_summary_log.parquet")

    if os.path.exists(monitor_summary_log_path):
        df_log = pd.read_parquet(monitor_summary_log_path)

        # 1. Last row (most recent location)
        try:
            return _coords_from_row(df_log.iloc[-1])
        except Exception as e:
            print(f"!! Could not read coords from last log row ({e}); trying first row.")

        # 2. First row
        try:
            return _coords_from_row(df_log.iloc[0])
        except Exception as e:
            print(f"!! Could not read coords from first log row ({e}); using hardcoded fallback.")
    else:
        print(f"!! No summary log found at {monitor_summary_log_path}; using hardcoded fallback.")

    # 3. Hardcoded fallback from config
    if fallback is None:
        raise ValueError(
            f"No fallback coordinates configured for monitor '{monitor_name}'. "
            f"Add an entry to monitor_coords in config.py."
        )
    return fallback

# ==========================================
# Processing Manifest Utilities
# ==========================================

def get_processing_manifest(processed_dir, monitor_name):
    """
    Loads the manifest parquet. If it doesn't exist, creates a new one.
    processed: means that we have sent the file to birdnet for analysis
    success: means that birdnet returned results for that file
    """
    manifest_path = os.path.join(processed_dir, monitor_name, "processing_manifest.parquet")
    print(f"Loading manifest from: {manifest_path}")
    
    if os.path.exists(manifest_path):
        return pd.read_parquet(manifest_path)
    
    # Create an empty manifest with the structure you requested
    return pd.DataFrame(columns=['file_name', 'processed', 'success', 'last_updated'])

def update_manifest(df_manifest, file_name, processed, success):
    """
    Updates or adds a file's status in the manifest.
    """
    from datetime import datetime
    
    new_row = {
        'file_name': file_name,
        'processed': processed,
        'success': success,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # If file exists, remove the old record before adding the new one
    df_manifest = df_manifest[df_manifest['file_name'] != file_name]
    df_manifest = pd.concat([df_manifest, pd.DataFrame([new_row])], ignore_index=True)
    
    return df_manifest

# ==========================================
# Consolidate Daily Parquets Utility
# ==========================================

def consolidate_daily_parquets(processed_dir, monitor_name):
    """
    Finds all daily recordings_batch_*.parquet files and merges them into a 
    single master file for the dashboard.
    uses glob and * to find all files matching the pattern.
    1. Path to where the daily files live
    2. Find all files
    3. Read and concatenate 
        - for each file in daily_files, read it as a dataframe and append to a list
        - then concatenate all dataframes in the list
    4. Save the master file
    """
    # 1. Path to where the daily files live
    search_path = os.path.join(processed_dir, monitor_name, "recordings_batch_*.parquet")
    master_output_path = os.path.join(processed_dir, monitor_name, "recordings_MASTER.parquet")
    
    # 2. Find all files
    daily_files = sorted(glob.glob(search_path))
    
    if not daily_files:
        print(f"No daily files found in {search_path}")
        return None

    print(f"Consolidating {len(daily_files)} files...")

    # 3. Read and concatenate
    df_list = [pd.read_parquet(f) for f in daily_files]
    df_master = pd.concat(df_list, ignore_index=True)

    # 4. Save the master file
    df_master.to_parquet(master_output_path, index=False)
    print(f"Success: Master file created with {len(df_master)} total detections.")

    csv_output_path = os.path.join(processed_dir, monitor_name, "recordings_MASTER.csv")
    df_master.to_csv(csv_output_path, index=False)
    print(f"Success: CSV export created at {csv_output_path}")

    return master_output_path