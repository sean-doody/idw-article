import pandas as pd

def load_data(data: str) -> pd.DataFrame:
    df = pd.read_csv(data)
    
    # ensure no missing doc IDs:
    assert len(df.loc[df["full_id"].isna()]) == 0, "Error: missing doc IDs found!"
    
    # check for null sentences:
    if len(df[df["text"].isna()]) != 0:
        N_OBSV = len(df)
        N_NULL = len(df[df["text"].isna()])
        print(f"Found {N_NULL} null rows: removing")
        df.dropna(inplace=True)
        assert len(df) == N_OBSV - N_NULL, "Error: length mismtach after removing null values!"
        df.reset_index(inplace=True, drop=True)
    
    print(f"Loaded dataset with {len(df)} rows")
    return df