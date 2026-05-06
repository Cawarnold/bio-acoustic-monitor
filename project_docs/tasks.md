# Bio-Acoustic Monitor — Project Tasks

A shared task list tracking active development work across the `nt-bird-detect` pipeline
and `nt-streamlit` dashboard repos.

---

## Sprint: 6 May – 20 May 2026
**Focus:** Bird species metadata feature — Wikipedia integration for the Streamlit dashboard

### Documentation
- [x] Created `nt-streamlit/docs/nt_streamlit_tdd.md` — full TDD for the Streamlit app including
      architecture, data schema, visualisations, deployment, and bird metadata feature
- [x] Updated `nt-bird-detect/docs/nt_birddetect_tdd.md` — added Section 7: Bird Species Metadata Feature
- [x] Created `project_docs/tasks.md` — project-level task tracking (this file)

### Implementation
- [x] 1. Create `bird_metadata.py` in `nt-streamlit/` with `get_bird_metadata(scientific_name)`:
         Wikipedia REST API fetch with `bird_metadata.json` local cache and `@st.cache_data(ttl=86400)`
- [x] 2. Create `prefetch_bird_metadata.py` standalone script:
         reads parquet, iterates unique scientific names, populates `bird_metadata.json` with 0.5s delay
- [x] 3. Add `render_bird_card(scientific_name)` to `bird_metadata.py`:
         `st.columns([1, 2])` layout with image, description, and Wikipedia attribution
- [x] 4. Wire `render_bird_card()` into `nt-streamlit/app.py` — Species Explorer selectbox
         after Top Species chart, renders card for selected species
- [x] 5. ~~Add `bird_metadata.json` to `nt-streamlit/.gitignore`~~ — reversed: file is committed to
         the repo so Streamlit Cloud can access the pre-warmed cache
- [x] 6. Add `requests` to `nt-streamlit/requirements.txt`
- [x] 7. Prefetch `bird_metadata.json` locally and pushed to GitHub — Streamlit Cloud redeployed

---

## Next Sprint: Friday 9 May 2026
- [ ] Review Python environment location — `.venv` currently lives in `nt-bird-detect/` but is
      shared with `nt-streamlit`. Decide whether each repo should have its own isolated env or
      whether a shared env at the `bio-acoustic-monitor/` project root makes more sense.
- [ ] Review species with no Wikipedia image — likely a scientific name formatting issue when
      querying the API. Identify which species return `None` and investigate whether name
      variants or redirects would resolve them.
- [x] Set default selection in Species Explorer dropdown to the top species by call count —
      so the bird card loads immediately on page open rather than requiring a manual selection.
