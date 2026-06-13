## Data Architecture & Pipeline

### 1. User Guide
a. Clone from repo
b. Copy data directory, with raw, processed, analytics directories inside from SSD or other location
    b.1 OR, set the `NT_DATA_DIR` env var to your data root (the folder containing `data/raw`, `data/processed`, `data/analytics`); optionally set `NT_MONITOR_NAME` to switch monitors. If unset, the pipeline falls back to the default Extreme SSD path.
       export NT_DATA_DIR="/Volumes/Extreme SSD/NatureThriveData"
       export NT_MONITOR_NAME="wrangcombe_audio1"
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
    tests/
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

### 3. Ingestion Layer (Raw)
This layer handles the movement of data from the field recorders into the local environment.

* **Current Status**: Manual ingestion. 
* **Process**: .wav files are moved to `data/raw/{monitor_name}/DataLoad_{date}/Data/`.
* **Future Automation**: Scripts will be added here to automate file transfers and verify data integrity before processing.

### 4. Processing Layer
The processing layer transforms raw audio into a structured, enriched master dataset.

#### Phase A: Acoustic Monitor Analysis (`process_audio_data_files.py`)
* **BirdNET Analysis**: Performs species detection on raw audio.
* **Daily Partitioning**: Results are saved into daily Parquet files (e.g., `detections_20260122.parquet`) for memory safety.
* **Manifest Control**: Uses `processing_manifest.parquet` to track progress and skip previously analyzed files.

#### Phase B: Engineering (`process_parquet_files.py`)
* **Consolidation**: Merges partitioned daily files into a single `recordings_batch_MASTER.parquet`.
* **CSV Export**: Also writes `recordings_MASTER.csv` to the same directory for sharing/external use.
* **Enrichment (Upcoming)**: Designated point for integrating secondary datasets, including GPS coordinates and weather data.
* **Normalization**: Ensures data types and schemas are consistent for the entire project history.

### 5. Aggregations & Analytics Layer
> **⚠️ Legacy / non-prod:** This layer was built to feed `nt-webapp`, which is currently shelved. The live Streamlit dashboard reads `recordings_MASTER.parquet` directly and aggregates on the fly, so these outputs are **not currently consumed**. Kept in case `nt-webapp` is resumed; the two known aggregation issues (see §10) are left unfixed for now.

This layer prepares the master data for high-speed retrieval by the dashboard.

* **Script**: `aggregations_analytics()` (called at the end of the Processing Layer).
* **Daily Stats**: Aggregates the Shannon Diversity Index and species richness per day.
* **Species Totals**: Calculates overall abundance counts for the species distribution charts.
* **Hourly Patterns**: Bins detections into 24-hour activity windows to visualize peak detection times.

### 6. Storage Tiers
| Tier | File Type | Logic |
| :--- | :--- | :--- |
| **Raw** | `.wav` | Unprocessed field recordings. Stored externally (~500GB, not in repo). |
| **Processed** | `detections_YYYYMMDD.parquet` / `MASTER.parquet` / `MASTER.csv` | Cleaned, consolidated data. Stored externally, not in repo. CSV produced alongside parquet for sharing. |
| **Analytics** | `species_totals` / `daily_unique_species` / `hourly_activity_patterns` / `csv/` | Pre-aggregated outputs. Stored externally in pipeline; copied to nt-streamlit for GitHub deployment. |

### 7. Workflow Execution Sequence
To update the dashboard with new field data, run the following in order:
1. `python src/processing/process_monitor_summary_log.py` (Processing Phase A - process monitor log)
2. `caffeinate -i python src/processing/process_audio_data_files.py` (Processing Phase A - process audio data)
    wrap command in caffeinate to keep laptop awake until script finishes
3. `python src/processing/process_parquet_files.py` (Processing Phase B - merge daily audio tables)
4. `python src/aggregations_analytics/aggregations_analytics.py` (Aggregations & Analytics - create summary tables)
5. copy master file to streamlit location
6. to view dashboard loaclly run `streamlit run app.py`



### 8. Testing
Tests live in `tests/` and use **pytest**. Run all tests with:
```
pytest tests/
```

#### Structure
| Folder | Covers |
| :--- | :--- |
| `tests/master_parquet/` | Integrity checks on `recordings_MASTER.parquet` |

#### `tests/master_parquet/` — Completeness Tests
* **test_not_empty**: Asserts the master file contains at least one row.
* **test_no_date_gaps**: Parses `file_date` (format `YYYYMMDD`) and asserts no missing dates between the earliest and latest recording.

### 9. Future Development

#### Auto-detect new DataLoad folders (`process_audio_data_files.py`)
* **Current behaviour**: `dataload_folder` is hardcoded on line 55 and must be manually updated each time a new DataLoad batch arrives.
* **Goal**: Automatically detect all unprocessed `DataLoad_*` folders by comparing folders in `data/raw/{monitor_name}/` against the processing manifest, and iterate over each one in date order.
* **Approach**: Replace the hardcoded `dataload_folder` with a loop that:
  1. Lists all `DataLoad_YYYYMMDD` folders in the raw monitor directory
  2. Checks the manifest to skip folders already fully processed
  3. Processes each unprocessed folder in chronological order

### 10. Code Improvements & Tech Debt
Observations from reviewing the pipeline scripts, utils, and tests. Captured as a backlog — not yet actioned.

#### Configuration & structure
* ✅ **Done** — Centralised all paths and the active monitor into `src/config.py`, imported by every entry-point script and by `tests/conftest.py`. The data root is overridable via the `NT_DATA_DIR` env var (monitor via `NT_MONITOR_NAME`) with a fallback default, so the SSD path is no longer baked into source. The duplicated config blocks and the dead `home_dir` line were removed.
* ⏸️ **Won't do (for now)** — Each script appends to `sys.path` manually to import `config`/`utils`. The "proper" fix is to make `src` an installed package (`pyproject.toml` + `pip install -e .`). Decided not worth it: the bootstrap works fine, and packaging would add an install step / change run commands for little practical gain on a single-developer project. Revisit if the project grows or needs CI.
* ⏸️ **Won't do — recommendation was flawed.** The original suggestion was to consolidate "scattered magic numbers" (`min_conf=0.5`, `confidence > 0.9`, `/ 24`) into shared constants. That advice misread the code: `min_conf=0.5` is the *detection floor* at ingestion (capture broadly) while `> 0.9` is a deliberately stricter *export filter* for shared CSVs — they are distinct decisions at distinct stages, not a duplicated value, so unifying them would be wrong. `/ 24` (hours per day) is self-evident in context. These literals are intentional and stay as-is.
* ⏸️ **Won't do — intentional.** `monitor_name` is a single explicit value per pipeline run, by design. Keeping it hardcoded/visible means you can glance at a script and know exactly which monitor it will process, rather than tracing dynamic multi-monitor logic. Readability for a human running the script wins over abstraction here.

#### Correctness / likely bugs
* ⏸️ **Won't fix — legacy (non-prod).** Two aggregations in `aggregations_analytics.py` are wrong relative to their comments: `daily_unique_species` takes `nunique('label')` within a `['file_date', 'label']` group (always 1), and `hourly_activity_patterns` groups by the full `file_time` (HHMMSS) rather than by hour. But this whole analytics/gold layer was built for **nt-webapp** (shelved); the Streamlit app reads `recordings_MASTER.parquet` directly and bins by hour itself, so nothing live consumes these. Left as-is — revisit if nt-webapp resumes. See §5.
* ⏸️ **Won't do — intentional.** Filename date/time parsing uses fixed string slices (`file[9:17]`, `file[18:24]`). The brittleness is the point: the SM4 recorder's filename format is fixed and known, so positional slicing is the simplest readable parse. If the format ever changes, this is *meant* to break so the change is noticed rather than silently absorbed. Revisit only if the recorder naming actually changes.
* 🔜 **Deferred to future pipeline work (see §9).** Consolidation currently just concatenates daily parquets — no de-duplication (re-running a day could double-count) and no dtype/schema normalisation (despite the "Normalization" note in Phase B). Both are intentionally left until the pipeline is extended to ingest a new `DataLoad_*` folder of `.wav` files, where handling re-processing and consistent schemas across batches becomes essential.
* ✅ **Done** — `get_monitor_coords` now tries the last log row, then the first row, then a per-monitor hardcoded fallback in `config.monitor_coords` (keyed by folder name), printing a warning at each fallback step. The magic coordinate literal was moved out of `utils` into `config.py`.

#### Robustness & operations
* Errors are caught with a broad `except Exception` that only prints — long overnight `caffeinate` runs have no log file, no log levels, and no way to distinguish a transient file error from a fatal one. Adopt the `logging` module writing to a timestamped log.
* The manifest is written to disk (`to_parquet`) on every single file iteration — heavy I/O over thousands of files. Write periodically (every N files) or on exit, while keeping crash-resilience.
* Within a day, each detection batch does a read-modify-write of the daily parquet (read existing → concat → rewrite), which grows quadratically as the day fills up — accumulate in memory and write once per day instead.
* `process_audio_data_files.py` writes into `PROCESSED_DATA_DIR/{monitor}/` without `os.makedirs(..., exist_ok=True)`; it only works because the summary-log script created the dir first — make it self-sufficient.
* BirdNET analysis is fully sequential; for ~500GB growing ~100GB/month, consider batching/parallelising the per-file analysis.

#### Testing
* Tests require the external SSD to be mounted (path hardcoded in `conftest.py`) and only cover MASTER completeness — none of the parsing, manifest, consolidation, or aggregation utils are tested.
* Add small committed sample fixtures so the suite can run in CI without the SSD.

#### Docs ↔ code drift (worth aligning)
* TDD refers to `detections_YYYYMMDD.parquet`, but the code writes `recordings_batch_YYYYMMDD.parquet`.
* Phase B mentions `recordings_batch_MASTER.parquet`; the code produces `recordings_MASTER.parquet`.
* TDD says the Analytics layer computes the **Shannon Diversity Index**, but no Shannon calculation exists in the code yet.
* TDD says `aggregations_analytics()` is "called at the end of the Processing Layer", but it is actually a standalone script run as a separate step (§7, step 4).
* Two requirements files exist (`requirements.txt` and `20260116_requirements.txt`) — clarify which is authoritative.

### 11. Deployment

Streamlit Community Cloud is free and connects directly to GitHub. Here's how to deploy:                          
                                                                                                                   
  1. Go to share.streamlit.io and sign in with your GitHub account                                                  
  2. Click New app
  3. Fill in:                                                                                                       
    - Repository: your-username/bio-acoustic-monitor
    - Branch: main                                                                                                  
    - Main file path: nt-streamlit/app.py                                                                           
  4. Click Deploy

