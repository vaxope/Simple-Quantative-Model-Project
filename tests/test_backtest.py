import yfinance as yf
import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal


from src.backtest.backtest import run_backtest, compute_backtest_metrics
from src.backtest.position_sizing import compute_position_size

def test_backtest_calc():
    df = pd.DataFrame({
        'ticker': ['AAA', 'AAA', 'AAA', 'AAA', 'AAA'],
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
