import json
import os
from datetime import datetime

import requests
import streamlit as st

CACHE_PATH = os.path.join(os.path.dirname(__file__), "bird_metadata.json")
WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
USER_AGENT = "BirdAcousticDashboard/1.0 (contact@example.com)"


def _load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


@st.cache_data(ttl=86400)
def get_bird_metadata(scientific_name: str) -> dict | None:
    cache = _load_cache()
    if scientific_name in cache:
        return cache[scientific_name]

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
        entry = {
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

    cache[scientific_name] = entry
    _save_cache(cache)
    return entry


def render_bird_card(scientific_name: str) -> None:
    metadata = get_bird_metadata(scientific_name)

    if not metadata:
        st.caption(f"No metadata available for _{scientific_name}_.")
        return

    thumbnail_url = metadata.get("thumbnail_url")
    col_img, col_text = st.columns([1, 2])

    if thumbnail_url:
        with col_img:
            st.image(thumbnail_url, width=200)

    text_col = col_text if thumbnail_url else col_img
    with text_col:
        st.markdown(f"**{metadata['common_name']}** _{metadata['scientific_name']}_")
        st.write(metadata.get("extract", ""))
        st.markdown(
            f"_Image and description from [Wikipedia]({metadata['wikipedia_url']}) | {metadata['license']}_"
        )
