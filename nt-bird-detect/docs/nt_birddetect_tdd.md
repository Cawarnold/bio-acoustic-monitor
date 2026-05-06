## Data Architecture & Pipeline

### 1. User Guide
a. Clone from repo
b. Copy data directory, with raw, processed, analytics directories inside from SSD or other location
    b.1 OR, Point the RAW_DATA_DIR to the location of 'Data' directory and the '*Summary.txt' file.
c. Build python environment
    brew install pyenv
    brew install ffmpeg
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
    echo 'eval "$(pyenv init -)"' >> ~/.zshrc
    source ~/.zshrc
    pyenv install 3.11.9
    cd /Users/cawa/Developer/Github/PersonalGithub/bio-acoustic-monitor/nt-bird-detect
    pyenv local 3.11.9
    python3 -m venv .venv
    source .venv/bin/activate 
    pip install --upgrade pip
    pip install birdnetlib librosa tensorflow ai_edge_litert resampy jupyterlab pyarrow
    -- note, might need to include 'pip install ffmpeg' here 
    pip install pandas dbt-duckdb
    pip install matplotlib plotly seaborn
    pip install streamlit pandas plotly pyarrow # for the streamlit app
    pip freeze > requirements.txt
d. To test env in ipynb
    python -m ipykernel install --user --name=nt-bird-detect --display-name "nt-bird-detect"
    then cmd+shift+p, (ensure vs code extensions are installed)
    might need a cmd+shift+p → Reload Window
e. Run 'Workflow Execution Sequence' below

### 2. Directory Structure
```
bio-acoustic-monitor/
  nt-bird-detect/           ← processing pipeline (this repo)
    src/
    docs/
    eda/
  nt-streamlit/             ← Streamlit dashboard (separate repo)
    data/                   ← analytics layer only, committed to GitHub
      wrangcombe_audio1/
        recordings_MASTER.parquet
    app.py
    requirements.txt

data/                       ← stored externally (SSD or separate local path)
  raw/                      ← .wav files (~500GB, growing ~100GB/month)
  processed/                ← daily parquets + MASTER.parquet
  analytics/                ← pre-aggregated parquet + csv outputs
```
After each pipeline run, copy `recordings_MASTER.parquet` from `data/processed/{monitor_name}/` into `nt-streamlit/data/{monitor_name}/` and push to trigger a Streamlit Cloud redeploy.

### 1. Ingestion Layer (Raw)
This layer handles the movement of data from the field recorders into the local environment.

* **Current Status**: Manual ingestion. 
* **Process**: .wav files are moved to `data/raw/{monitor_name}/DataLoad_{date}/Data/`.
* **Future Automation**: Scripts will be added here to automate file transfers and verify data integrity before processing.

### 2. Processing Layer
The processing layer transforms raw audio into a structured, enriched master dataset.

#### Phase A: Acoustic Monitor Analysis (`process_audio_data_files.py`)
* **BirdNET Analysis**: Performs species detection on raw audio.
* **Daily Partitioning**: Results are saved into daily Parquet files (e.g., `detections_20260122.parquet`) for memory safety.
* **Manifest Control**: Uses `processing_manifest.parquet` to track progress and skip previously analyzed files.

#### Phase B: Engineering (`process_parquet_files.py`)
* **Consolidation**: Merges partitioned daily files into a single `recordings_batch_MASTER.parquet`.
* **Enrichment (Upcoming)**: Designated point for integrating secondary datasets, including GPS coordinates and weather data.
* **Normalization**: Ensures data types and schemas are consistent for the entire project history.

### 3. Aggregations & Analytics Layer
This layer prepares the master data for high-speed retrieval by the dashboard.

* **Script**: `aggregations_analytics()` (called at the end of the Processing Layer).
* **Daily Stats**: Aggregates the Shannon Diversity Index and species richness per day.
* **Species Totals**: Calculates overall abundance counts for the species distribution charts.
* **Hourly Patterns**: Bins detections into 24-hour activity windows to visualize peak detection times.

### 4. Storage Tiers
| Tier | File Type | Logic |
| :--- | :--- | :--- |
| **Raw** | `.wav` | Unprocessed field recordings. Stored externally (~500GB, not in repo). |
| **Processed** | `detections_YYYYMMDD.parquet` / `MASTER.parquet` | Cleaned, consolidated data. Stored externally, not in repo. |
| **Analytics** | `species_totals` / `daily_unique_species` / `hourly_activity_patterns` / `csv/` | Pre-aggregated outputs. Stored externally in pipeline; copied to nt-streamlit for GitHub deployment. |

### 5. Workflow Execution Sequence
To update the dashboard with new field data, run the following in order:
1. `python src/processing/process_monitor_summary_log.py` (Processing Phase A - process monitor log)
2. `caffeinate -i python src/processing/process_audio_data_files.py` (Processing Phase A - process audio data)
    wrap command in caffeinate to keep laptop awake until script finishes
3. `python src/processing/process_parquet_files.py` (Processing Phase B - merge daily audio tables)
4. `python src/aggregations_analytics/aggregations_analytics.py` (Aggregations & Analytics - create summary tables)
5. copy master file to streamlit location
6. to view dashboard loaclly run `streamlit run app.py`



### 6. Deployment

Streamlit Community Cloud is free and connects directly to GitHub. Here's how to deploy:                          
                                                                                                                   
  1. Go to share.streamlit.io and sign in with your GitHub account                                                  
  2. Click New app
  3. Fill in:                                                                                                       
    - Repository: your-username/bio-acoustic-monitor
    - Branch: main                                                                                                  
    - Main file path: nt-streamlit/app.py                                                                           
  4. Click Deploy

---

### 7. Bird Species Metadata Feature

Enriches the Streamlit dashboard with Wikipedia-sourced images and descriptions for each detected species.

#### Cache File: `bird_metadata.json`
Stored in `nt-streamlit/` and committed to the repo. Pre-warm by running
`prefetch_bird_metadata.py` locally before deploying, then commit alongside the code.
Keyed by scientific name, each entry contains:
```json
{
  "common_name": "European Robin",
  "scientific_name": "Erithacus rubecula",
  "extract": "The European robin is...",
  "thumbnail_url": "https://upload.wikimedia.org/...",
  "wikipedia_url": "https://en.wikipedia.org/wiki/European_robin",
  "license": "CC BY-SA 3.0",
  "fetched_at": "2026-05-06T12:00:00"
}
```

#### Fetching Logic: `get_bird_metadata(scientific_name: str) -> dict | None`
- Checks `bird_metadata.json` first; returns cached entry if found (no API call)
- On cache miss, calls `GET https://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name_underscored}`
  with `User-Agent: "BirdAcousticDashboard/1.0 (contact@example.com)"`
- Extracts: `extract`, `thumbnail.source`, `content_urls.desktop.page`, license (default `"CC BY-SA 3.0"`)
- Merges new entry into `bird_metadata.json` and returns it
- Returns `None` gracefully on API failure or missing thumbnail
- Decorated with `@st.cache_data(ttl=86400)` — runs once per species per Streamlit session day

#### Pre-warming Script: `prefetch_bird_metadata.py`
- Reads the parquet file (path configurable at top of script)
- Iterates all unique scientific names, skipping those already cached
- Prints progress per species; adds 0.5s delay between API calls
- Saves completed `bird_metadata.json`

#### Display Component: `render_bird_card(scientific_name: str)`
- Calls `get_bird_metadata()` and renders via `st.columns([1, 2])`
  - Left: `st.image(thumbnail_url, width=200)`
  - Right: bold common + scientific name, extract text, and attribution:
    `_Image and description from [Wikipedia](url) | CC BY-SA 3.0_`
- Graceful fallbacks: text-only if no thumbnail, placeholder message if no metadata
- Wired into the existing species display area — no dashboard restructuring                