import yfinance as yf
import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal
from pytest import approx


from src.backtest.backtest import run_backtest, compute_backtest_metrics
from src.backtest.position_sizing import compute_position_size

def test_backtest_calc():
    df = pd.DataFrame({
        "ticker": ["AAA"] * 5,
        'date': pd.date_range('2023-01-01', periods=5),
        "return": [np.nan, 0.10, 0.10, 0.10, 0.127],
        'position': [1.0, 1.0, 1.5, 0.9, 1.8]
    })
    
    result = run_backtest(df, 'position', 'return')
    
    expected_gross = pd.Series([np.nan, 0.1000, 0.1000, 0.1500, 0.1143], name='gross_return')
    expected_turnover = pd.Series([np.nan, np.nan, 0, 0.5, 0.6], name='turnover')
    expected_cost = pd.Series([np.nan, np.nan, 0, 0.00025, 0.0003], name='cost')
    expected_net_return = pd.Series([np.nan, np.nan, 0.1000, 0.14975, 0.114], name='net_return')
    
    assert_series_equal(result['gross_return'], expected_gross)
    assert_series_equal(result['turnover'], expected_turnover)
    assert_series_equal(result['cost'], expected_cost)
    assert_series_equal(result['net_return'], expected_net_return)

def test_backtest_cross_ticker_leakage():
    dates = list(pd.date_range("2023-01-01", periods=5)) * 2
    df = pd.DataFrame({
        "ticker": ["AAA"] * 5 + ["BBB"] * 5,
        "date": dates,
        "return": [np.nan, 0.10, 0.10, 0.10, 0.127, np.nan, 0.11, 0.11, 0.11, 0.128],
        'position': [1.0, 1.0, 1.5, 0.9, 1.8, 1.1, 1.1, 1.6, 1.0, 1.9]
    })
    
    result = run_backtest(df, 'position', 'return')
    
    # Index 5 must leak not AAA's last position into position_lagged
    assert pd.isna(result.loc[5, "position_lagged"])
    assert pd.isna(result.loc[5, "gross_return"])
    assert pd.isna(result.loc[5, "turnover"])
    assert pd.isna(result.loc[5, "cost"])
    assert pd.isna(result.loc[5, "net_return"])
    
    # Position_lagged  has to be BBB's postion[5], 1.1, not AAA's position[4], 1.8
    assert result.loc[6, "position_lagged"] == 1.1
    
    # Must not calcualte diff across tickers
    assert pd.isna(result.loc[6, "turnover"])
    assert pd.isna(result.loc[6, "cost"])
    assert pd.isna(result.loc[6, "net_return"])
    
    assert result.loc[7, "position_lagged"] == 1.1
    assert result.loc[7, "turnover"] == 0.0
    assert result.loc[7, "cost"] == 0.0
    assert result.loc[7, "net_return"] == approx(1.1 * 0.11 - 0.0)