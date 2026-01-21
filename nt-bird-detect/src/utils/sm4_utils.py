import pandas as pd
import os

def parse_sm4_summary(base_folder):
    """
    Looks for the SM4 .txt summary file in the base_folder 
    and returns it as a Pandas DataFrame.
    """
    # Find any file ending in .txt
    files = [f for f in os.listdir(base_folder) if f.endswith('.txt')]
    
    if not files:
        print(f"!! No .txt file found in {base_folder}")
        return None

    txt_path = os.path.join(base_folder, files[0])
    
    # Read the data, skipping the extra spaces after commas
    df = pd.read_csv(txt_path, skipinitialspace=True)
    return df