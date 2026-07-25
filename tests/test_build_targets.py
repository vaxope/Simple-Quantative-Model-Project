from src.data.targets.build_targets import add_volatility_target, add_direction_target
from src.data.features.build_features import load_prices_long, add_log_returns
import numpy as np
import pandas as pd

def test_volatility_target_calc():
    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    returns = [0.01, -0.02, 0.015, 0.005, -0.01, 0.02, -0.015, 0.01, 0.0, 0.008]
    df = pd.DataFrame({
        "ticker": ["AAA"] * 10,
        "date": dates,
        "log_return": returns,
    })

    horizon = 5
    df = add_volatility_target(df, horizons=[horizon])

    # At row 0, target_vol_5d should reflect returns[1:6] (the next 5 days after day 0)
    future_window = np.array(returns[1:6])
    expected_std = np.std(future_window, ddof=1)
    expected_vol = np.log(expected_std * np.sqrt(252))

    actual = df.iloc[0]['target_vol_5d']
    assert np.isclose(actual, expected_vol)

def test_log_volatility_targ_calc_ticker_leakage():
    # Create synthetic two-ticker dataset with sequential dates
    dates = pd.date_range("2020-01-01", periods=10, freq="B")
    df = pd.DataFrame({
        "ticker": ["AAPL"] * 10 + ["GOOG"] * 10,
        "date": list(dates) + list(dates),
        "log_return": [0.01 * (i + 1) for i in range(20)],
    })

    horizon = 5
    df = add_volatility_target(df, horizons=[horizon])

    # Extract target values for each ticker group
    aapl_targets = df.query("ticker == 'AAPL'")['target_vol_5d']
    goog_targets = df.query("ticker == 'GOOG'")['target_vol_5d']

    # Last h rows of GOOG should be nan
    assert aapl_targets.iloc[-horizon:].isna().all(), (
        "Last h rows of AAPL should be NaN, but found leaked values from GOOG!"
    )

    # Last h rows of AAPL should be nan
    assert goog_targets.iloc[-horizon:].isna().all(), (
        "Last h rows of GOOG should be NaN due to lack of future data!"
    )

    # Check valid target values exist before the final h rows
    assert aapl_targets.iloc[:-horizon].notna().all()
    assert goog_targets.iloc[:-horizon].notna().all()

def test_direction_target_calc_synthetic():
    dates = pd.date_range("2020-01-01", periods=4, freq="B")
    returns = [0.01, -0.005, 0.02, -0.01]
    df = pd.DataFrame({
        "ticker": ["AAA"] * 4,
        "date": dates,
        "log_return": returns,
    })

    df = add_direction_target(df, horizons=[1])

    # Row 0's target should reflect row 1's return (-0.005, i.e. down -> 0.0)
    assert df.iloc[0]['target_dir_1d'] == 0.0
    # Row 1's target should reflect row 2's return (0.02, i.e. up -> 1.0)
    assert df.iloc[1]['target_dir_1d'] == 1.0
    # Last row has no future data
    assert pd.isna(df.iloc[3]['target_dir_1d'])

def test_direction_target_ticker_leakage():
    tickers = ['AAPL', 'GOOG']
    df = load_prices_long("data/raw_prices.parquet", tickers)
    df = add_log_returns(df)

    horizon = 1
    df = add_direction_target(df, horizons=[horizon])

    # Filter per ticker
    aapl_targets = df.query("ticker == 'AAPL'")['target_dir_1d']
    goog_targets = df.query("ticker == 'GOOG'")['target_dir_1d']

    # Last row of AAPL must be NaN (must not leak into GOOG's first return)
    assert aapl_targets.iloc[-horizon:].isna().all(), (
        "Last row of AAPL should be NaN, but leaked data from GOOG!"
    )

    # Last row of GOOG must also be NaN
    assert goog_targets.iloc[-horizon:].isna().all(), (
        "Last row of GOOG should be NaN due to lack of future data!"
    )

    # All earlier rows should have valid target values
    assert aapl_targets.iloc[:-horizon].notna().all()
    assert goog_targets.iloc[:-horizon].notna().all()