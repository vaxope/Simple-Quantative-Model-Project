import pandas as pd
import numpy as np

def add_volatility_target(df: pd.DataFrame, horizons: list[int] = [5], return_col: str = 'log_return') -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(by=['ticker', 'date'])
    
    for h in horizons:
        col_name = f'target_vol_{h}d'

        # Shift by -h to move past values into future
        df[col_name] = df.groupby('ticker')[return_col].transform(
            lambda x: np.log((x.rolling(window=h).std() * np.sqrt(252)).shift(-h))
        )
        
    return df

def add_direction_target(df: pd.DataFrame, horizons: list[int] = [1], return_col: str = 'log_return') -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(by=['ticker', 'date'])

    for h in horizons:
        col_name = f'target_dir_{h}d'

        # Shift by -h to move past values into future
        future_return = df.groupby('ticker')[return_col].shift(-h)

        df[col_name] = np.where(
            future_return.isna(), np.nan, (future_return > 0).astype(float)
        )

    return df