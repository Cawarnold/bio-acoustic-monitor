import pandas as pd
import os

def parse_sm4_summary(raw_monitor_path, monitor_name):
    """
    Finds all 'DataLoad_YYYYMMDD' folders and extracts metadata.
    In each folder, find the .txt summary file
    and add monitor/file metadata columns,
    then return it as a Pandas DataFrame.
    """
    all_dataframes = []

    # 1. Look for folders starting with 'DataLoad'
    dataload_folders = [f for f in os.listdir(raw_monitor_path) 
                        if os.path.isdir(os.path.join(raw_monitor_path, f)) 
                        and f.startswith('DataLoad')]

    for folder in dataload_folders:
        load_date = folder.replace('DataLoad_', '') # Extract '20260121'
        folder_path = os.path.join(raw_monitor_path, folder)
        
        # 2. Look for the .txt file inside that specific DataLoad folder
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        
        for file_name in txt_files:
            txt_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(txt_path, skipinitialspace=True)

            # 3. Add the columns you requested
            df['monitor_name'] = monitor_name
            df['dataload_batch'] = folder      # e.g., DataLoad_20260121
            df['load_date'] = load_date        # e.g., 20260121
            df['source_file'] = file_name
            
            all_dataframes.append(df)
            print(f"Successfully parsed {file_name} from {folder}")

    if not all_dataframes:
        return None
        
    return pd.concat(all_dataframes, ignore_index=True)