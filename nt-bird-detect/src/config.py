import os

# ==========================================
# Central configuration for the nt-bird-detect pipeline
# ==========================================
# All entry-point scripts import paths and the active monitor from here, so the
# external data location and monitor name are defined in exactly one place.

# Project root (this file lives in <root>/src/config.py)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# External data root. Override with the NT_DATA_DIR env var so the SSD path is
# not baked into source; falls back to the default SSD mount.
DATA_DIR = os.environ.get("NT_DATA_DIR", "/Volumes/Extreme SSD/NatureThriveData")

RAW_DATA_DIR = os.path.join(DATA_DIR, "data/raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "data/processed")
ANALYTICS_DATA_DIR = os.path.join(DATA_DIR, "data/analytics")

# ==========================================
# Pipeline profile: "prod" (default) or "test"
# ==========================================
# Set NT_ENV=test (e.g. via `run.sh test`) to run the whole pipeline against the
# test monitor and batch instead of production. Both profiles' values are kept
# here, side by side. Outputs are keyed by monitor_name, so a test run never
# touches the production folders.
ENV = os.environ.get("NT_ENV", "prod")

if ENV == "test":
    monitor_name = "test_audio1"
    dataload_folder = "DataLoad_20260612"
else:
    monitor_name = "wrangcombe_audio1"
    dataload_folder = "DataLoad_20260428"

# Fallback field-site coordinates (lat, lon) per monitor, keyed by the monitor's
# folder name. Used only as a last resort when the summary log has no usable
# coordinates (see get_monitor_coords). Add an entry here for each new monitor.
monitor_coords = {
    "wrangcombe_audio1": (50.9481, -3.2503),
    "test_audio1": (50.9481, -3.2503),  # placeholder (same as wrangcombe) — test only
    "test_audio2": (50.9481, -3.2503),  # placeholder (same as wrangcombe) — test only
}
