import time
import os
import glob
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = "/app/data"

@app.route('/api/time')
def get_current_time():
    """Useful for infrastructure testing"""
    return {'time': time.time()}

@app.route('/api/summary')
def get_bird_summary():
    """Fetches real bird count data from the Gold Layer"""
    search_pattern = os.path.join(DATA_DIR, "*.parquet")
    files = glob.glob(search_pattern)
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)