FROM apache/airflow:3.1.7

# Add package dependencies - these will be available to all Airflow tasks
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir apache-airflow==${AIRFLOW_VERSION} -r /requirements.txt
