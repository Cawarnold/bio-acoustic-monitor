# Bio-Acoustic Monitor — Project Tasks

A shared task list tracking active development work across the `nt-bird-detect` pipeline
and `nt-streamlit` dashboard repos.

---

## Sprint: 6 May – 20 May 2026
**Focus:** Bird species metadata feature — Wikipedia integration for the Streamlit dashboard

- [ ] 1. Create `bird_metadata.py` in `nt-streamlit/` with `get_bird_metadata(scientific_name)`:
         Wikipedia REST API fetch with `bird_metadata.json` local cache and `@st.cache_data(ttl=86400)`
- [ ] 2. Create `prefetch_bird_metadata.py` standalone script:
         reads parquet, iterates unique scientific names, populates `bird_metadata.json` with 0.5s delay
- [ ] 3. Add `render_bird_card(scientific_name)` to `bird_metadata.py`:
         `st.columns([1, 2])` layout with image, description, and Wikipedia attribution
- [ ] 4. Wire `render_bird_card()` into `nt-streamlit/app.py` at the species display point
- [x] 5. ~~Add `bird_metadata.json` to `nt-streamlit/.gitignore`~~ — reversed: file is committed to
         the repo so Streamlit Cloud can access the pre-warmed cache
