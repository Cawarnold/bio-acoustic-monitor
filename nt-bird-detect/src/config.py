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

# Active monitor. Override with the NT_MONITOR_NAME env var.
monitor_name = os.environ.get("NT_MONITOR_NAME", "wrangcombe_audio1")
