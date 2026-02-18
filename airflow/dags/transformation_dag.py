from airflow.sdk import dag, task
from pendulum import datetime
import subprocess
import os

# Default settings for the pipeline
@dag(
    dag_id="nature_thrive_monitor",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",  # Runs once a day
    catchup=False,      # Don't run for past dates
    tags=["bioacoustic", "naturethrive"],
)
def bio_acoustic_monitor_pipeline():

    #@task
    #def process_audio_data_files():
    #    """Runs the BirdNET analysis on raw audio files."""
    #    # We use the path inside the container
    #    script_path = "/opt/airflow/src/process_audio_data_files.py"
    #    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    #    print(result.stdout)
    #    if result.returncode != 0:
    #        raise Exception(f"process_audio_data_files failed: {result.stderr}")

    @task
    def process_parquet_files():
        script_path = "/opt/airflow/src/processing/process_parquet_files.py"
        
        # We add /opt/airflow/src to the PYTHONPATH so 'import utils' works
        env = os.environ.copy()
        env["PYTHONPATH"] = "/opt/airflow/src"

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            cwd="/opt/airflow/src", # Run from the root of your code
            env=env                 # Pass the new PYTHONPATH
        )
    
        print(result.stdout)
        if result.returncode != 0:
            raise Exception(f"Failed: {result.stderr}")

    # Set the dependency: Phase A must finish before Phase B starts
    #process_audio_data_files() >> 
    process_parquet_files()

# Instantiate the DAG
bio_acoustic_monitor_pipeline()