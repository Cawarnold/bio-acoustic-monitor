import numpy as np
import pandas as pd


# ==========================================
# Aggregate Daily and Hourly Analytics Utilities
# ==========================================

def aggregate_daily_species(df_detections):
    """
    Summarizes total counts for each species per day.
    """
    # Group by Date and Species name, then count
    daily_summary = df_detections.groupby(['file_date', 'label']).agg(count=('label', 'count')).reset_index()
    return daily_summary

def aggregate_hourly_activity(df_detections):
    """
    Groups detections by hour of the day (00-23).
    """
    # Extract the hour (first two digits of HHMMSS)
    df_detections['hour'] = df_detections['file_time'].str[:2]

    hourly_summary = df_detections.groupby(['hour', 'label']).agg(count=('label', 'count')).reset_index()
    return hourly_summary

def calculate_diversity_metrics(df):
    """
    Calculates richness and Shannon Diversity Index (H).
    """
    if df.empty:
        return 0, 0
    
    # Species Richness: number of unique species
    richness = df['label'].nunique()
    
    # Shannon Index Calculation
    counts = df['label'].value_counts()
    total = len(df)
    probs = counts / total
    shannon_h = -np.sum(probs * np.log(probs))
    
    return richness, round(shannon_h, 2)

def aggregate_daily_stats(df):
    """
    Creates a summary of counts and diversity per day.
    """
    # Group by date to get daily counts
    daily_groups = df.groupby('file_date')
    
    daily_data = []
    for date, group in daily_groups:
        richness, shannon = calculate_diversity_metrics(group)
        daily_data.append({
            'date': date,
            'total_detections': len(group),
            'species_richness': richness,
            'shannon_index': shannon
        })
    
    return pd.DataFrame(daily_data)