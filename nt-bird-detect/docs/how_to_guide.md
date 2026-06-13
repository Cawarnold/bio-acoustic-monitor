## How To Guide

### 1. Activate the Environment

From the project root:
```
cd /Users/cawa/Developer/Github/PersonalGithub/bio-acoustic-monitor/nt-bird-detect
source .venv/bin/activate
```
You should see `(.venv)` in your terminal prompt.

---

### 2. Run the Pipeline

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
`~/Developer/Projects_NotesData/NT(bio-acoustic-monitor)/data/processed/wrangcombe_audio1/`

**Step 4 — Generate aggregations and analytics**
```
python src/aggregations_analytics/aggregations_analytics.py
```

**Step 5 — Copy master file to Streamlit repo**

Copy `recordings_MASTER.parquet` from `data/processed/wrangcombe_audio1/` into `nt-streamlit/data/wrangcombe_audio1/` and push to trigger a Streamlit Cloud redeploy.

---

### 3. Run Tests

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
`~/Developer/Projects_NotesData/NT(bio-acoustic-monitor)/data/processed/tests/missing_dates.csv`
