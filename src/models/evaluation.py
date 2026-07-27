import numpy as np
import pandas as pd

# Evaluates MAE, RMSE, and directional accuracy if applicable
def evaluate_predictions(y_true: pd.Series, y_pred: pd.Series, baseline_for_direction: pd.Series = None,) -> pd.Series:
    y_true = pd.Series(y_true).reset_index(drop=True)
    y_pred = pd.Series(y_pred).reset_index(drop=True)

    # MAE and RMSE
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

    metrics = {"RMSE": rmse, "MAE": mae}

    # Directional accuracy is applicable
    if baseline_for_direction is not None:
        base = pd.Series(baseline_for_direction).reset_index(drop=True)
        actual_change = np.sign(y_true - base)
        pred_change = np.sign(y_pred - base)
        metrics["Directional_Accuracy"] = np.mean(actual_change == pred_change)

    return pd.Series(metrics)

# Returns a list of train_dates and test_dates pairs for sliding window for walk-forwad validation
def walk_forward_folds(df: pd.DataFrame, date_col: str = 'date', train_size: int = 252, test_size = 21, step: int = None) -> list[tuple[np.ndarray, np.ndarray]]:
    # Step defaults to test_size so tests windows are contiguous
    if step is None:
        step = test_size

    # Multiple rows share the same same trading date so this ensures all tickers stay together in the same fold
    unique_dates = np.sort(df[date_col].unique())
    n = len(unique_dates)

    folds = []
    start = 0

    # Sliding window
    while start + train_size + test_size <= n:
        train_dates = unique_dates[start: start + train_size]
        test_dates = unique_dates[start + train_size : start + train_size + test_size]
        folds.append((train_dates, test_dates))
        start += step

    return folds