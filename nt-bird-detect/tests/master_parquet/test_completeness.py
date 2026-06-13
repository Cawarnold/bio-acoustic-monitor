import os
import pandas as pd

def test_not_empty(df_master):
    assert len(df_master) > 0

def test_no_date_gaps(df_master, processed_data_dir):
    dates = pd.to_datetime(df_master['file_date'], format='%Y%m%d').dt.date.unique()
    full_range = pd.date_range(start=min(dates), end=max(dates), freq='D').date
    missing = sorted(set(full_range) - set(dates))

    if missing:
        tests_dir = os.path.join(processed_data_dir, 'tests')
        os.makedirs(tests_dir, exist_ok=True)
        pd.DataFrame({'missing_date': missing}).to_csv(
            os.path.join(tests_dir, 'missing_dates.csv'), index=False
        )

    assert not missing, f"Missing {len(missing)} date(s) — see data/processed/tests/missing_dates.csv"
