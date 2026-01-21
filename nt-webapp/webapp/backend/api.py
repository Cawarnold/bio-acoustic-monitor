import time
import os
import glob
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 1. DIRECTORY CONFIGURATION
# ==========================================

### location of analytics data files in docker container
    # mapped from nt-bird-detect project via docker-compose.yml
    # - ../../nt-bird-detect/data/analytics:/app/data/analytics:ro
#DATA_DIR = "app/data/analytics"

# ==========================================
# 1. DIRECTORY CONFIGURATION
# ==========================================

### Project Root Discovery
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../")) 

### Base Data Directories
ANALYTICS_DATA_DIR = ("/app/data/analytics")
monitor_name = "wrangcombe_audio1"


# ==========================================
# 2. API ENDPOINTS
# ==========================================

@app.route('/api/time')
def get_current_time():
    """Useful for infrastructure testing"""
    return {'time': time.time()}

@app.route('/api/summary')
def get_bird_summary():
    """Fetches real bird count data from the Gold Layer"""
    files = glob.glob(os.path.join(ANALYTICS_DATA_DIR, "*.parquet"))
    
    # Safety check: only call max() if files exist
    DATA_PATH = max(files, key=os.path.getctime) if files else None

    # Now check if DATA_PATH is None OR if the file somehow doesn't exist
    if not DATA_PATH or not os.path.exists(DATA_PATH):
        # Fallback for testing if the Parquet file isn't there yet
        return jsonify([
            {"file_date": "2026-01-18", "bird_name": "Owl says data is not available", "call_counts": 5},
            {"file_date": "2026-01-19", "bird_name": "Robin says go check parquet file", "call_counts": 12}
        ])
    
    try:
        df = pd.read_parquet(DATA_PATH)
        data = df.to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/daily-stats')
def get_daily_stats():
    """Fetches Daily Diversity and Shannon Index"""
    path = os.path.join(ANALYTICS_DATA_DIR, monitor_name, "daily_summary.parquet")
    if not os.path.exists(path):
        return jsonify({"error": f"File not found at: {path}"}), 404
    
    df = pd.read_parquet(path)
    return df.to_json(orient='records')

@app.route('/api/species-totals')
def get_species_totals():
    """Fetches Total Detections per Species"""
    path = os.path.join(ANALYTICS_DATA_DIR, monitor_name, "species_totals.parquet")
    if not os.path.exists(path):
        return jsonify({"error": f"File not found at: {path}"}), 404
    
    df = pd.read_parquet(path)
    return df.to_json(orient='records')

@app.route('/api/hourly-patterns')
def get_hourly_activity_patterns():
    """Fetches Hourly Activity Patterns"""
    path = os.path.join(ANALYTICS_DATA_DIR, monitor_name, "hourly_activity_patterns.parquet")
    if not os.path.exists(path):
        return jsonify({"error": f"File not found at: {path}"}), 404
    
    df = pd.read_parquet(path)
    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)