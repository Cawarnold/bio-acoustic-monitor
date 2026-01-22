import os
import glob

import numpy as np
import pandas as pd


# ==========================================
# Aggregations and Analytics Utilities
# ==========================================

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
    
    daily_stats = pd.DataFrame(daily_data)
    return daily_stats