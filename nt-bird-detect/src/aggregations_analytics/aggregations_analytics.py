import os
import sys

import pandas as pd


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
from utils.analytics_gold_utils import (
    aggregate_daily_species,
    aggregate_daily_stats,
    aggregate_hourly_activity
)

# ==========================================
# 3. Function to process recordings and create analytics
# ==========================================

def aggregations_analytics():
    monitor_name = "wrangcombe_audio1"
    processed_recordings_path = os.path.join(PROCESSED_DATA_DIR, monitor_name, "recordings_batch.parquet")
    analytics_dir = os.path.join(ANALYTICS_DATA_DIR, monitor_name)
    
    # Ensure analytics directory exists
    os.makedirs(analytics_dir, exist_ok=True)

    if not os.path.exists(processed_recordings_path):
        print("!! No processed data found to aggregate.")
        return

    # Load the processed_recordings file
    df = pd.read_parquet(processed_recordings_path)

    # 1. DAILY STATS (For line charts: Activity over time)
    df_daily = aggregate_daily_stats(df)
    df_daily.to_parquet(os.path.join(analytics_dir, "daily_summary.parquet"), index=False)

    # 2. SPECIES TOTALS (For pie/bar charts: What's out there?)
    df_species = df.groupby('label').agg(count=('label', 'count')).reset_index()
    df_species.to_parquet(os.path.join(analytics_dir, "species_totals.parquet"), index=False)

    # 3. HOURLY PATTERNS (For heatmaps: When are they singing?)
    df_hourly = aggregate_hourly_activity(df)
    df_hourly.to_parquet(os.path.join(analytics_dir, "hourly_activity_patterns.parquet"), index=False)

    print(f"--- SUCCESS: aggregations_analytics layers created in {analytics_dir} ---")

# ==========================================
# 4. RUN THE FUNCTION
# ==========================================

if __name__ == "__main__":
    aggregations_analytics()