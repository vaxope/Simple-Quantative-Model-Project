from src.data.targets.build_targets import add_volatility_target, add_direction_target
from src.data.features.build_features import load_prices_long, add_log_returns
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def test_log_volatility_targ_calc():
    tickers = ['GOOG', 'AAPL']
    df = load_prices_long("data/raw_prices.parquet", tickers)
    df = add_log_returns(df)
    df = add_volatility_target(df)

    # Looks at log_returns from Google from 01/13/2020 - 01/17/2020 (11-12 aren't trading days)
    returns_array = df.query("ticker == 'GOOG' and '2020-01-13' <= date <= '2020-01-17'")['log_return'].to_numpy()

    # Calculates log volatility target from log_returns from that timeframe
    sample_std = np.std(returns_array, ddof=1)
    annualized_vol = sample_std * np.sqrt(252)
    log_vol_target = np.log(annualized_vol)

    target_date = pd.Timestamp("2020-01-10")
    actual_target = df.query("ticker == 'GOOG' and date == @target_date")['target_vol_5d'].iloc[0]

    assert np.isclose(log_vol_target, actual_target)

def test_log_volatility_targ_calc_ticker_leakage():
    pass