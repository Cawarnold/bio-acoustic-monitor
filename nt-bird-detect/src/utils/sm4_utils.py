import os

import pandas as pd

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

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
        
        # 2. Look for the .txt file inside that specific DataLoad folder
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        
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

def get_monitor_coords(processed_dir, monitor_name):
    """
    Reads the processed summary log to find coordinates.
    """
    monitor_summary_log_path = os.path.join(processed_dir, monitor_name, "monitor_summary_log.parquet")
    
    if os.path.exists(monitor_summary_log_path):
        df_log = pd.read_parquet(monitor_summary_log_path)
        # We take the last recorded location in the log
        latest_entry = df_log.iloc[-1]
        
        lat = float(latest_entry['LAT'])
        lon = float(latest_entry['LON'])
        
        # Adjust longitude if it is marked as West
        if str(latest_entry['EW']).strip().lower() == 'w':
            lon = -abs(lon)
            
        return lat, lon
    
    # Fallback if no log is found
    print(f"!! No summary log found at {monitor_summary_log_path}. Using defaults.")
    return 50.9481, -3.2503

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
