import os
import sys


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

# ==========================================
# 2. Import utility functions
# ==========================================

# Add src to path so we can import our utils
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
from utils.sm4_utils import parse_sm4_summary


# ==========================================
# 3. Function to parse summary file
# ==========================================

def run_summary_log_processing():
    print("--- Starting Monitor Summary Log Processing ---")
    
    # Define the specific monitor we are working on
    monitor_name = "wrangcombe_audio1"
    
    # Input path: data/raw/wrangcombe_audio1/
    raw_monitor_path = os.path.join(RAW_DATA_DIR, monitor_name)

    # Output path: data/processed/wrangcombe_audio1/monitor_summary_log.parquet
    output_dir = os.path.join(PROCESSED_DATA_DIR, monitor_name)
    output_file = os.path.join(output_dir, "monitor_summary_log.parquet")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Call the utility function with the monitor name
    df = parse_sm4_summary(raw_monitor_path, monitor_name)
    
    if df is not None:
        print("\nPreview of combined data:")
        print(df.head(5))
        
        # Save to Parquet format
        df.to_parquet(output_file, index=False)
        print(f"\n--- SUCCESS ---")
        print(f"Combined {len(df)} rows from all DataLoad batches.")
        print(f"Saved metadata to: {output_file}")

# ==========================================
# 4. RUN THE FUNCTION
# ==========================================

if __name__ == "__main__":
    run_summary_log_processing()