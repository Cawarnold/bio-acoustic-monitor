## How To Guide

### 1. Activate the Environment

> **Before anything else:** Make sure the SSD is mounted. All pipeline data lives at
> `/Volumes/Extreme SSD/NatureThriveData`. If the drive isn't connected, scripts will fail.

From the project root:
```
cd /Users/cawa/Developer/Github/PersonalGithub/bio-acoustic-monitor/nt-bird-detect
source .venv/bin/activate
```
You should see `(.venv)` in your terminal prompt.

---

### 2. How to Read the Code

Every pipeline stage is split across **two files**. To understand any step, read them in this order:

**1. `src/config.py` — the settings.**
This is the single place that holds every environment/location value the pipeline uses:
- `DATA_DIR` — the data root (the SSD path), overridable via the `NT_DATA_DIR` env var.
- `RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `ANALYTICS_DATA_DIR` — derived from `DATA_DIR`.
- `monitor_name` — which monitor the run targets (e.g. `wrangcombe_audio1`), overridable via `NT_MONITOR_NAME`.

If you want to know *where* data is read/written or *which monitor* is being processed, this is the only file you need to check. Change a value here and it applies across every script.

**2. The script for that stage — the recipe.**
Each entry-point script (`src/processing/*.py`, `src/aggregations_analytics/*.py`) reads top-to-bottom as the steps for that stage. It imports the values it needs from `config.py` at the top, so the logic stays uncluttered by long paths. Anything hardcoded *inside* a script (e.g. `dataload_folder`, `min_conf`) is deliberately kept local to that step, so it's visible exactly where it is used rather than hidden behind an abstraction.

**Mental model:** `config.py` = *the settings*, the script = *the recipe*. Read config first to know the inputs, outputs, and target monitor; then read the script to follow what happens to them.

---

### 3. Run the Pipeline

Run the following scripts in order from the project root:

**Step 1 — Process monitor summary log**
```
python src/processing/process_monitor_summary_log.py
```

**Step 2 — Run BirdNET audio analysis** (wrap in `caffeinate` to keep laptop awake)
```
caffeinate -i python src/processing/process_audio_data_files.py
```

**Step 3 — Merge daily parquets into master file**
```
python src/processing/process_parquet_files.py
```
Outputs `recordings_MASTER.parquet` and `recordings_MASTER.csv` to:
`/Volumes/Extreme SSD/NatureThriveData/data/processed/wrangcombe_audio1/`

**Step 4 — Generate aggregations and analytics**
```
python src/aggregations_analytics/aggregations_analytics.py
```

**Step 5 — Copy master file to Streamlit repo**

Copy `recordings_MASTER.parquet` from `data/processed/wrangcombe_audio1/` into `nt-streamlit/data/wrangcombe_audio1/` and push to trigger a Streamlit Cloud redeploy.

---

### 4. Run Tests

From the project root with `.venv` active:
```
python -m pytest tests/ -v
```

#### What the tests check
| Test | File | Description |
| :--- | :--- | :--- |
| `test_not_empty` | `recordings_MASTER.parquet` | Asserts the master file contains at least one row |
| `test_no_date_gaps` | `recordings_MASTER.parquet` | Checks for missing dates between first and last recording |

If date gaps are found, a CSV is exported to:
`/Volumes/Extreme SSD/NatureThriveData/data/processed/tests/missing_dates.csv`
