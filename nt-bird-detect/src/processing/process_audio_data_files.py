import os
import sys
from datetime import datetime
import pandas as pd
from birdnetlib.analyzer import Analyzer

# ==========================================
# 1. DIRECTORY CONFIGURATION
# ==========================================

### Project Root Discovery
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # dir of this file
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../")) # root dir of project

### Base Data Directories
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")
ANALYTICS_DATA_DIR = os.path.join(PROJECT_ROOT, "data/analytics")

# SETUP VARIABLES
monitor_name = "wrangcombe_audio1"

# ==========================================
# 2. Import utility functions
# ==========================================

# Add src to path so we can import our utils
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
from utils.processing_silver_utils import (
    analyze_audio_file, 
    get_monitor_coords, 
    get_processing_manifest, 
    update_manifest
)

# ==========================================
# 3. Function to process audio files
# ==========================================

def run_audio_analysis():
    print("--- Starting BirdNET Audio Analysis ---")

    # Update this to the specific DataLoad folder you want to process
    dataload_folder = "DataLoad_20260121"
    
    # Use the coordinates from your SM4 log
    lat, lon = get_monitor_coords(PROCESSED_DATA_DIR, monitor_name)
    print(f"Using coordinates from log: Lat {lat}, Lon {lon}")
    
    # Minimum confidence threshold for BirdNET detections
    min_conf = 0.5

    recordings_dir = os.path.join(RAW_DATA_DIR, monitor_name, dataload_folder, "Data")
    #output_path = os.path.join(PROCESSED_DATA_DIR, monitor_name, "recordings_batch.parquet")
    manifest_path = os.path.join(PROCESSED_DATA_DIR, monitor_name, "processing_manifest.parquet")

    # Initialize Analyzer once
    analyzer = Analyzer()
    
    # Check if recordings directory exists (eg. wrangcombe_audio1/DataLoad_20260121/Data)
    if not os.path.exists(recordings_dir):
        print(f"!! Directory not found: {recordings_dir}")
        return

    # Get sorted list of audio files
    entries = sorted(os.listdir(recordings_dir))
    counter = 0

    # Load manifest or create it - to check if file has already been processed
    df_manifest = get_processing_manifest(PROCESSED_DATA_DIR, monitor_name)
    print(df_manifest.head())

    # Process each audio file
    for file in entries:
        if not file.lower().endswith('.wav'): continue
        
        counter += 1
    
        # check if we have already processed this file using the manifest
        print(f"Checking manifest for: {file}")
        if not df_manifest.empty and file in df_manifest['file_name'].values:
            if df_manifest.loc[df_manifest['file_name'] == file, 'processed'].iloc[0] == 1:
                print(f"Skipping (Already Processed): {file}")
                continue

        # Full path to audio file
        file_path = os.path.join(recordings_dir, file)

        # Parse date from filename
        try:
            raw_date, raw_time = file[9:17], file[18:24]   # YYYYMMDD, HHMMSS 
            file_year, file_month, file_day = int(file[9:13]), int(file[13:15]), int(file[15:17]) # YYYY, MM, DD
            file_date_obj = datetime(year=file_year, month=file_month, day=file_day)
            
            # Define output path - daily parquet file
            daily_output_path = os.path.join(PROCESSED_DATA_DIR, monitor_name, f"recordings_batch_{raw_date}.parquet")

            print(f"[{counter}/{len(entries)}] Analyzing: {file}")
            
            # Call utility function to analyze audio file
            detections = analyze_audio_file(analyzer, file_path, lat, lon, file_date_obj, min_conf)

            # Determine success (were birds found?)
            has_output = 1 if len(detections) > 0 else 0

            # Convert detections data into DataFrame and add metadata
            if has_output:
                df_current = pd.DataFrame(detections)
                df_current['file_name'] = file
                df_current['file_date'] = raw_date
                df_current['file_time'] = raw_time
                df_current['monitor_name'] = monitor_name
                df_current['dataload_batch'] = dataload_folder
                
                if os.path.exists(daily_output_path):
                    df_existing = pd.read_parquet(daily_output_path)
                    df_combined = pd.concat([df_existing, df_current], ignore_index=True)
                else:
                    df_combined = df_current
                
                df_combined.to_parquet(daily_output_path, index=False)
                print(f"-> Saved {len(detections)} detections to {os.path.basename(daily_output_path)}")
            
            # Update manifest (In-Memory)
            df_manifest = update_manifest(df_manifest, file, processed=1, success=has_output)
            df_manifest.to_parquet(manifest_path, index=False)
            print(df_manifest.tail(5))

        except Exception as e:
            print(f"!! Error with {file}: {e}")
            df_manifest = update_manifest(df_manifest, file, processed=1, success=0)
            df_manifest.to_parquet(manifest_path, index=False)

    print("\n--- Audio analysis batch complete ---")

# ==========================================
# 4. RUN THE FUNCTION
# ==========================================

if __name__ == "__main__":
    run_audio_analysis()