import os
import sys
import pandas as pd
import glob

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

# Define the specific monitor we are working on
monitor_name = "wrangcombe_audio1"

# ==========================================
# 2. Import utility functions
# ==========================================

# Add src to path for imports
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
from utils.processing_silver_utils import (
    consolidate_daily_parquets
)

# ==========================================
# 3. Functions to run on parquet files
# ==========================================

def run_data_processing():
    print("--- Starting Post-Analysis Data Processing ---")
    
    # STEP 1: CONSOLIDATION
    # Uses the utility function to merge detections_*.parquet into MASTER.parquet
    print(f"Executing consolidation for: {monitor_name}")
    master_file = consolidate_daily_parquets(PROCESSED_DATA_DIR, monitor_name)
    
    if master_file:
        print(f"Step 1 Complete: {os.path.basename(master_file)} generated.")
    
    # STEP 2: FUTURE TABLE JOINS (Placeholder)
    # print("Step 2: Joining with secondary data tables...")
    # This is where we will add the code for your upcoming data merges.

    print("--- All Data Processing Tasks Complete ---")

# ==========================================
# 4. RUN THE FUNCTION
# ==========================================

if __name__ == "__main__":
    run_data_processing()