#!/usr/bin/env bash
#
# Run the full nt-bird-detect pipeline against production or test data.
#
# Usage:
#   ./run.sh prod    # production monitor (wrangcombe_audio1)   [default]
#   ./run.sh test    # test monitor (test_audio1, 4-file batch)
#
# The ONLY difference between the two is NT_ENV, which config.py reads to pick the
# monitor + DataLoad batch. Outputs are keyed by monitor, so a test run never
# touches production folders. This script just orchestrates the existing scripts.

set -euo pipefail

# Run from the project root (where this script lives) so src/ paths resolve.
cd "$(dirname "$0")"

PROFILE="${1:-prod}"
if [[ "$PROFILE" != "prod" && "$PROFILE" != "test" ]]; then
    echo "Usage: ./run.sh [prod|test]"
    exit 1
fi

# Activate the project venv if it isn't already active.
if [[ -z "${VIRTUAL_ENV:-}" && -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi

export NT_ENV="$PROFILE"
echo "=== nt-bird-detect pipeline | NT_ENV=$NT_ENV ==="

python src/processing/process_monitor_summary_log.py
caffeinate -i python src/processing/process_audio_data_files.py
python src/processing/process_parquet_files.py
python src/aggregations_analytics/aggregations_analytics.py

echo "=== Pipeline complete | NT_ENV=$NT_ENV ==="
