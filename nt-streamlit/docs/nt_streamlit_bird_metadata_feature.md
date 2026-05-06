I have a Streamlit dashboard app that reads bird acoustic monitor data from a parquet file. 
The parquet contains columns: date, time, common_name, scientific_name, confidence, filename.

I want to add bird images and descriptions sourced from the Wikipedia REST API.

## Goal
For each unique bird species displayed in the dashboard, show:
- A photo of the bird
- A short description
- Attribution: link to Wikipedia page + "CC BY-SA" license text

## Implementation: Option A (live API) with Option B hybrid (local cache)

### Cache file
Create/maintain a file called `bird_metadata.json` in the project root.
It is a dict keyed by scientific name (e.g. "Erithacus rubecula"), each value being:
{
  "common_name": "European Robin",
  "scientific_name": "Erithacus rubecula",
  "extract": "The European robin is...",
  "thumbnail_url": "https://upload.wikimedia.org/...",
  "wikipedia_url": "https://en.wikipedia.org/wiki/European_robin",
  "license": "CC BY-SA 3.0",
  "fetched_at": "2026-05-06T12:00:00"
}

### Fetching logic
Write a function `get_bird_metadata(scientific_name: str) -> dict | None` that:
1. Checks bird_metadata.json for an existing entry for that scientific name
2. If found, returns it (no API call)
3. If not found, calls the Wikipedia REST API:
   GET https://en.wikipedia.org/api/rest_v1/page/summary/{scientific_name_underscored}
   with header: User-Agent: "BirdAcousticDashboard/1.0 (contact@example.com)"
4. If the API returns a valid response (status 200), extracts:
   - extract (the text summary)
   - thumbnail.source (image URL)
   - content_urls.desktop.page (Wikipedia URL)
   - license defaulting to "CC BY-SA 3.0"
5. Saves the new entry to bird_metadata.json (merging with existing entries)
6. Returns the metadata dict
7. If the API call fails or returns no thumbnail, returns None gracefully

Wrap the fetch function with @st.cache_data(ttl=86400) so it only runs once 
per species per day within a Streamlit session.

### Pre-warming utility
Also write a standalone script called `prefetch_bird_metadata.py` that:
- Reads the parquet file (path configurable at top of script)
- Gets all unique scientific names
- Calls get_bird_metadata() for each one not already in bird_metadata.json
- Prints progress (e.g. "Fetching Erithacus rubecula... done")
- Adds a 0.5s delay between API calls to be polite to Wikipedia
- Saves the completed bird_metadata.json

### Streamlit display component
Write a function `render_bird_card(scientific_name: str)` that:
- Calls get_bird_metadata()
- If metadata is found, renders using st.columns([1, 2]):
  - Left column: st.image() with the thumbnail_url, width=200
  - Right column: bold common + scientific name, extract text, 
    and attribution as small italic markdown: 
    "Image and description from [Wikipedia](url) | CC BY-SA 3.0"
- If no metadata found, shows a placeholder message
- Handles missing thumbnail gracefully (show text only)

### Notes
- bird_metadata.json should be added to .gitignore if not already there
- The parquet file path should come from whatever config/variable is already 
  used in the existing dashboard code — don't hardcode it
- Don't restructure the existing dashboard, just add the new function and 
  wire render_bird_card() into wherever individual species are displayed