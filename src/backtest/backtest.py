import pandas as pd
import numpy as np

def run_backtest(df: pd.DataFrame, position_col: str, return_col: str = 'log_return', cost_bps: float = 5.0) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(['ticker', 'date']) # Ensures rows are chronologically ordered

    # Lag position by 1 so today's decided position earns tommorow's returns
    df['position_lagged'] = df.groupby('ticker')[position_col].shift(1)

    df['gross_return'] = df['position_lagged'] * df[return_col]

    # Calculates how much position changed from prior period
    df['turnover'] = df.groupby('ticker')['position_lagged'].diff().abs()
    df['cost'] = df['turnover'] * (cost_bps / 10000)

    df['net_return'] = df['gross_return'] - df['cost']

    return df

def compute_backtest_metrics(net_returns: pd.Series, periods_per_year: int = 252) -> pd.Series:
    net_returns = net_returns.dropna()

    # Check if empty after dropping
    if net_returns.empty:
        return pd.Series(
            {
                "Annualized Return": np.nan,
                "Sharpe": np.nan,
                "Max_Drawdown": np.nan,
                "Calmar ratio": np.nan,
            }
        )
        
    # Risk adjusted performance
    sharpe = net_returns.mean() / net_returns.std() * np.sqrt(252)

    # Cumulative returns over time
    cum_ret = (1 + net_returns).cumprod()
    running_max = cum_ret.cummax()
    drawdown = cum_ret / running_max - 1
    
    # How far strategy dropped from peak at every point
    max_dd = drawdown.min()
    
    # Annual return and calamar ratio
    num_years = len(net_returns) / periods_per_year
    ann_return = (cum_ret.iloc[-1]) ** (1/periods_per_year) - 1 if num_years > 0 else np.nan

    calamar = ann_return / abs(max_dd) if abs(max_dd) > 0 else (np.nan if np.isnan(ann_return) else np.inf)
    
    

    return pd.Series({'Annualized Return': ann_return, 'Sharpe': sharpe, 'Max Drawdown': max_dd, 'Calmar Ratio': calamar})


    