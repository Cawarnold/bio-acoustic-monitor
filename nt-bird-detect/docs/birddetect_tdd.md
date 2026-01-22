## 🏗️ Data Architecture & Pipeline

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
| **Raw** | `.wav` | Unprocessed field recordings (Excluded from Git). |
| **Processed** | `detections_YYYYMMDD.parquet` / `MASTER.parquet` | Cleaned, consolidated, and enriched detection data. |
| **Analytics** | `daily_stats` / `species_totals` / `hourly` | Pre-aggregated JSON/Parquet tables optimized for UI performance. |

### 5. Workflow Execution Sequence
To update the dashboard with new field data, run the following in order:
1. `python src/process_monitor_summary_log.py` (Processing Phase A - process monitor log)
2. `python src/process_audio_data_files.py` (Processing Phase A - process audio data)
3. `python src/process_parquet_files.py` (Processing Phase B - merge daily audio tables)
4. `python src/aggregations_analytics.py` (Aggregations & Analytics - create summary tables)