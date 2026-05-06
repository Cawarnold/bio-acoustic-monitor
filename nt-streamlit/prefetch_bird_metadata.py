import time
from datetime import datetime

import pandas as pd
import requests

from bird_metadata import CACHE_PATH, USER_AGENT, WIKIPEDIA_API, _load_cache, _save_cache

PARQUET_PATH = "streamlit_data/wrangcombe_audio1/recordings_MASTER.parquet"
DELAY_SECONDS = 0.5


def fetch_from_wikipedia(scientific_name: str) -> dict | None:
    name_underscored = scientific_name.replace(" ", "_")
    url = WIKIPEDIA_API.format(name_underscored)
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        thumbnail_url = data.get("thumbnail", {}).get("source")
        if not thumbnail_url:
            return None
        return {
            "common_name": data.get("title", scientific_name),
            "scientific_name": scientific_name,
            "extract": data.get("extract", ""),
            "thumbnail_url": thumbnail_url,
            "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "license": "CC BY-SA 3.0",
            "fetched_at": datetime.utcnow().isoformat(),
        }
    except Exception:
        return None


if __name__ == "__main__":
    df = pd.read_parquet(PARQUET_PATH)
    scientific_names = df["scientific_name"].dropna().unique().tolist()
    cache = _load_cache()

    to_fetch = [n for n in scientific_names if n not in cache]
    print(f"Found {len(scientific_names)} unique species. {len(to_fetch)} not yet cached.")

    for name in to_fetch:
        print(f"Fetching {name}...", end=" ", flush=True)
        entry = fetch_from_wikipedia(name)
        if entry:
            cache[name] = entry
            print("done")
        else:
            print("no data")
        time.sleep(DELAY_SECONDS)

    _save_cache(cache)
    print(f"\nCache saved to {CACHE_PATH} ({len(cache)} entries total)")
