import pandas as pd

def split_by_date(df: pd.DataFrame, train_end: str, val_end: str, date_col: str = "date",) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Splits df into train/val/test using same cutoff date across all tickers
    df = df.copy()
    train_end = pd.Timestamp(train_end)
    val_end = pd.Timestamp(val_end)

    train = df[df[date_col] <= train_end]
    val = df[(df[date_col] > train_end) & (df[date_col] <= val_end)]
    test = df[df[date_col] > val_end]

    return train, val, test