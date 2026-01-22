import os
import glob

import numpy as np
import pandas as pd


# ==========================================
# Aggregations and Analytics Utilities
# ==========================================

def calculate_species_daily_profiles(df):
    """
    Calculates Abundance, Occupancy, and Certainty per species per day.
    Abundance	Total Call Count
    Occupancy	% of 1 hour blocks occupied by this species
    Certainty	Average Confidence Score
    """

    if df.empty:
        return pd.DataFrame()

    # 1. Ensure hour is available
   # Ensure file_time is a string padded to 6 digits (HHMMSS)
    df['file_time'] = df['file_time'].astype(str).str.zfill(6)
    df['hour'] = df['file_time'].str[:2].astype(int)

    # 2. Group and aggregate in one clean step
    df_profiles = df.groupby(['file_date', 'label']).agg(
        calls=('label', 'count'),              # Total abundance
        hours_active=('hour', 'nunique'),      # Count unique hours (how many hours had detections from this species)
        occupancy_pct=('hour', lambda x: round((x.nunique() / 24) * 100, 2)),  # Occupancy percentage
        confidence=('confidence', 'mean'),      # Mean certainty
        max_confidence=('confidence', 'max')    # Max certainty
    ).reset_index()

    return df_profiles