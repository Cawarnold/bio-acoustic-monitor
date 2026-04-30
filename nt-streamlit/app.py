import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Bio-Acoustic Monitor", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "streamlit_data")
monitor_name = "wrangcombe_audio1"


@st.cache_data
def load_data():
    path = os.path.join(DATA_DIR, monitor_name, "recordings_MASTER.parquet")
    df = pd.read_parquet(path)
    df['file_date'] = pd.to_datetime(df['file_date'], format='%Y%m%d')
    df['hour'] = df['file_time'].astype(str).str.zfill(6).str[:2].astype(int)
    return df


st.title("Bio-Acoustic Monitor Dashboard")
st.caption(f"Monitor: {monitor_name}")

try:
    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    min_conf = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.5, 0.05)
    date_range = st.sidebar.date_input("Date Range", [df['file_date'].min(), df['file_date'].max()])

    df_filtered = df[
        (df['confidence'] >= min_conf) &
        (df['file_date'] >= pd.to_datetime(date_range[0])) &
        (df['file_date'] <= pd.to_datetime(date_range[1]))
    ]

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Detections", f"{len(df_filtered):,}")
    col2.metric("Unique Species", df_filtered['common_name'].nunique())
    col3.metric("Recording Days", df_filtered['file_date'].nunique())
    col4.metric("Date Range", f"{df_filtered['file_date'].min().strftime('%d %b')} – {df_filtered['file_date'].max().strftime('%d %b %Y')}")

    st.divider()

    # Top species
    st.subheader("Top Species by Call Count")
    top_n = st.slider("Show top N species", 5, 30, 15)
    df_species = df_filtered.groupby('common_name').size().reset_index(name='count').sort_values('count', ascending=True).tail(top_n)
    fig = px.bar(df_species, x='count', y='common_name', orientation='h', labels={'count': 'Detections', 'common_name': ''})
    st.plotly_chart(fig, use_container_width=True)

    # Daily detections
    st.subheader("Daily Detections")
    df_daily = df_filtered.groupby('file_date').size().reset_index(name='count')
    fig2 = px.line(df_daily, x='file_date', y='count', labels={'file_date': 'Date', 'count': 'Detections'})
    st.plotly_chart(fig2, use_container_width=True)

    # Hourly heatmap
    st.subheader("Hourly Activity by Species")
    top_species = df_filtered['common_name'].value_counts().head(15).index
    df_hourly = df_filtered[df_filtered['common_name'].isin(top_species)].groupby(['hour', 'common_name']).size().reset_index(name='count')
    fig3 = px.density_heatmap(df_hourly, x='hour', y='common_name', z='count', labels={'hour': 'Hour of Day', 'common_name': 'Species', 'count': 'Detections'})
    st.plotly_chart(fig3, use_container_width=True)

    # Raw data
    with st.expander("View raw data"):
        st.dataframe(df_filtered[['file_date', 'file_time', 'common_name', 'scientific_name', 'confidence', 'file_name']].head(500), use_container_width=True)

except FileNotFoundError:
    st.error("No data found. Copy recordings_MASTER.parquet into the data/ directory.")
