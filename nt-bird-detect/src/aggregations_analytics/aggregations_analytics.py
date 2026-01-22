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

# Define the specific monitor we are working on
monitor_name = "wrangcombe_audio1"

# ==========================================
# 2. Import utility functions
# ==========================================

# Add src to path so we can import our utils
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
from utils.analytics_gold_utils import (
    aggregate_daily_species,
    aggregate_daily_stats,
    aggregate_daily_unique_species,
    aggregate_hourly_activity
)

# ==========================================
# 3. Function to process recordings and create analytics
# ==========================================

def aggregations_analytics():
    #monitor_name = "wrangcombe_audio1"
    processed_recordings_path = os.path.join(PROCESSED_DATA_DIR, monitor_name, "recordings_batch_MASTER.parquet")
    analytics_dir = os.path.join(ANALYTICS_DATA_DIR, monitor_name)
    
    # Ensure analytics directory exists
    os.makedirs(analytics_dir, exist_ok=True)

    if not os.path.exists(processed_recordings_path):
        print("!! No processed data found to aggregate.")
        return

    # Load the processed_recordings file
    df = pd.read_parquet(processed_recordings_path)

    # SPECIES TOTALS (For pie/bar charts: What's out there?)
    df_species_totals = df.groupby('label').agg(count=('label', 'count')).reset_index()
    df_species_totals.to_parquet(os.path.join(analytics_dir, "species_totals.parquet"), index=False)

    # DAILY UNIQUE SPECIES (For stacked area charts: Diversity over time)
    df_daily_unique_species = df.groupby(['file_date', 'label']).agg(count=('label', 'nunique')).reset_index()
    df_daily_unique_species.to_parquet(os.path.join(analytics_dir, "df_daily_unique_species.parquet"), index=False)

    # HOURLY PATTERNS (For heatmaps: When are they singing?)
    df_hourly_activity_patterns = df.groupby(['file_time', 'label']).agg(count=('label', 'count')).reset_index()
    df_hourly_activity_patterns.to_parquet(os.path.join(analytics_dir, "hourly_activity_patterns.parquet"), index=False)

    # DAILY STATS (For line charts: Activity over time)
    df_daily_diversity = aggregate_daily_stats(df)
    df_daily_diversity.to_parquet(os.path.join(analytics_dir, "daily_diversity.parquet"), index=False)

    print(f"--- SUCCESS: aggregations_analytics layers created in {analytics_dir} ---")

# ==========================================
# 4. RUN THE FUNCTION
# ==========================================

if __name__ == "__main__":
    aggregations_analytics()