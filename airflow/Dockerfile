FROM apache/airflow:3.1.7

# Add any additional system dependencies if needed (e.g., for audio processing)
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends libsndfile1 ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER airflow

# Add package dependencies - these will be available to all Airflow tasks
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir apache-airflow==${AIRFLOW_VERSION} -r /requirements.txt

# Install the specific TensorFlow version that BirdNET needs 
# as a separate layer to prevent conflict with the main build.
RUN pip install --no-cache-dir tensorflow-cpu==2.15.0