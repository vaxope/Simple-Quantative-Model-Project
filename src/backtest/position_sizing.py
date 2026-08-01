import pandas as pd
import numpy as np

def compute_position_size(predicted_log_vol: pd.Series, target_vol: float = 0.15, max_leverage: float = 2.0) -> pd.Series:
    # Convert log-volatility back to standardized annualzied volatility and computes exposure weight
    predicted_vol = np.exp(predicted_log_vol)
    size = target_vol / predicted_vol
    # Clipped so output weight doesn't exceed max_leverage 
    return size.clip(upper = max_leverage) 