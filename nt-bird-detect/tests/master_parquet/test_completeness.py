import pandas as pd

def test_not_empty(df_master):
    assert len(df_master) > 0

def test_no_date_gaps(df_master):
    dates = pd.to_datetime(df_master['file_date'], format='%Y%m%d').dt.date.unique()
    full_range = pd.date_range(start=min(dates), end=max(dates), freq='D').date
    missing = sorted(set(full_range) - set(dates))
    assert not missing, f"Missing {len(missing)} date(s): {missing}"
