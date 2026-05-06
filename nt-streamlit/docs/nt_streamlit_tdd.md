## nt-streamlit — Technical Design Document

### 1. Overview
A Streamlit dashboard that visualises bird acoustic detection data collected by the `nt-bird-detect`
processing pipeline. It reads a consolidated parquet file and renders interactive charts for species
activity, daily trends, and hourly patterns. A Wikipedia metadata integration (in development) will
enrich each species entry with images and descriptions.

### 2. Directory Structure
```
nt-streamlit/
├── app.py                        ← main Streamlit application
├── requirements.txt              ← streamlit, pandas, plotly, pyarrow
├── docs/
│   ├── nt_streamlit_tdd.md       ← this document
│   └── nt_streamlit_bird_metadata_feature.md  ← Wikipedia feature spec
└── streamlit_data/
    └── {monitor_name}/
        └── recordings_MASTER.parquet   ← committed to GitHub for Streamlit Cloud
```

### 3. Data Source
The dashboard reads `streamlit_data/{monitor_name}/recordings_MASTER.parquet`, produced by the
`nt-bird-detect` processing pipeline and copied here manually after each pipeline run.

| Column | Type | Notes |
| :--- | :--- | :--- |
| `file_date` | int (YYYYMMDD) | Converted to datetime on load |
| `file_time` | int (HHMMSS) | Hour extracted as `hour` column on load |
| `common_name` | str | English species name |
| `scientific_name` | str | Latin species name |
| `confidence` | float | BirdNET detection confidence (0.0–1.0) |
| `file_name` | str | Source .wav filename |

### 4. Configuration
| Variable | Value | Purpose |
| :--- | :--- | :--- |
| `DATA_DIR` | `./streamlit_data` | Root directory for parquet data |
| `monitor_name` | `"wrangcombe_audio1"` | Subdirectory identifying the monitor site |

### 5. Application Architecture (`app.py`)

#### Data Loading
`load_data()` — decorated with `@st.cache_data`. Reads the parquet, converts `file_date` to datetime,
and derives an integer `hour` column from `file_time`. Raises `FileNotFoundError` if parquet is absent.

#### Sidebar Filters
Applied to all charts and metrics:
- **Min Confidence**: slider 0.0–1.0, default `0.9`, step `0.05`
- **Date Range**: date picker defaulting to full date span of the dataset

#### Overview Metrics
Four columns rendered at the top of the page:
| Metric | Source |
| :--- | :--- |
| Total Detections | `len(df_filtered)` |
| Unique Species | `df_filtered['common_name'].nunique()` |
| Recording Days | `df_filtered['file_date'].nunique()` |
| Date Range | min/max formatted as `dd Mon – dd Mon YYYY` |

#### Visualisations
| Chart | Type | Details |
| :--- | :--- | :--- |
| Top Species by Call Count | Horizontal bar | Configurable N (5–30, default 15), sorted ascending |
| Daily Detections | Line chart | Grouped by `file_date` |
| Hourly Activity | Bar chart | All species, grouped by `hour` (0–23) |
| Hourly Activity by Species | Heatmap (imshow) | Top 15 species, row-normalised, Viridis colour scale |

#### Raw Data View
Collapsed `st.expander` showing first 500 rows of filtered data with columns:
`file_date`, `file_time`, `common_name`, `scientific_name`, `confidence`, `file_name`.

#### Error Handling
Wraps all dashboard content in a `try/except FileNotFoundError` block — displays a user-friendly
`st.error` message if the parquet file is missing.

### 6. Deployment
Hosted on Streamlit Community Cloud, connected directly to this GitHub repository.

| Setting | Value |
| :--- | :--- |
| Repository | `bio-acoustic-monitor` |
| Branch | `main` |
| Main file path | `nt-streamlit/app.py` |

To update the live dashboard: copy the latest `recordings_MASTER.parquet` from the pipeline's
`data/processed/{monitor_name}/` into `nt-streamlit/streamlit_data/{monitor_name}/` and push to
`main`. Streamlit Cloud redeploys automatically on push.

---

### 7. Bird Species Metadata Feature

Enriches the dashboard with Wikipedia-sourced images and descriptions for each detected species.

#### Cache File: `bird_metadata.json`
Stored in the `nt-streamlit` project root and committed to the repo. Pre-warm by running
`prefetch_bird_metadata.py` locally before deploying, then commit the file alongside the code.
Keyed by scientific name:
```json
{
  "Erithacus rubecula": {
    "common_name": "European Robin",
    "scientific_name": "Erithacus rubecula",
    "extract": "The European robin is...",
    "thumbnail_url": "https://upload.wikimedia.org/...",
    "wikipedia_url": "https://en.wikipedia.org/wiki/European_robin",
    "license": "CC BY-SA 3.0",
    "fetched_at": "2026-05-06T12:00:00"
  }
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
Standalone script to populate the cache before deploying:
- Reads parquet from the path defined at the top of the script
- Iterates all unique scientific names, skipping those already in `bird_metadata.json`
- Prints progress per species; adds 0.5s delay between API calls
- Saves completed `bird_metadata.json`

#### Display Component: `render_bird_card(scientific_name: str)`
Renders a species card using `st.columns([1, 2])`:
- **Left**: `st.image(thumbnail_url, width=200)`
- **Right**: bold common + scientific name, extract text, and attribution:
  `_Image and description from [Wikipedia](url) | CC BY-SA 3.0_`
- Graceful fallbacks: text-only if no thumbnail; placeholder message if no metadata found
- Wired into the existing species display area — no restructuring of `app.py`
