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

# Runs walk_forward with a model
def run_walk_forward(df: pd.DataFrame, feature_cols: list[str], target_col: str, model_factory, train_size: int = 252, test_size: int = 21, step: int = None) -> pd.DataFrame:
    # Generates folds
    folds = walk_forward_folds(df, train_size=train_size, test_size=test_size, step=step)
    results = []

    for i, (train_dates, test_dates) in enumerate(folds):
        """
        Pulls all rows matching training or testing dates across all tickers
        There are NaNs in the beginning and end, so we drop them to prevent model errors
        """
        train_df = df[df['date'].isin(train_dates)].dropna(subset=feature_cols + [target_col])
        test_df = df[df['date'].isin(test_dates)].dropna(subset=feature_cols + [target_col])

        # Skip fold if data preparation leaves empty set, which can happen when features are stil warming up
        if train_df.empty or test_df.empty:
            continue

        # Creates brand new untrained model instance and fits data
        X_train, y_train = train_df[feature_cols], train_df[target_col]
        X_test, y_test = test_df[feature_cols], test_df[target_col]

        model = model_factory()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        # Checks for overfitting
        metrics = evaluate_predictions(y_test, preds)
        metrics["test_rmse"] = metrics["RMSE"]
        train_preds = model.predict(X_train)
        train_metrics = evaluate_predictions(y_train, train_preds)
        metrics["train_rmse"] = train_metrics["RMSE"]

        # Calculates metrics and attaches fold numbers and exact start/end dates
        metrics['folds'] = i
        metrics['train_start'], metrics['train_end'] = train_dates[0], train_dates[-1]
        metrics['test_start'], metrics['test_end'] = test_dates[0], test_dates[-1]
        results.append(metrics)

    return pd.DataFrame(results)

def get_walk_forward_predictions(df: pd.DataFrame, feature_cols: list[str], target_col: str, model_factory, train_size: int = 252, test_size: int = 21, step: int = None) -> pd.DataFrame:
    # Generates folds
    folds = walk_forward_folds(df, train_size=train_size, test_size=test_size, step=step)
    oof_preds = []
    
    for train_dates, test_dates in folds:
        """
        Pulls all rows matching training or testing dates across all tickers
        There are NaNs in the beginning and end, so we drop them to prevent model errors
        """
        train_df = df[df['date'].isin(train_dates)].dropna(subset=feature_cols + [target_col])
        test_df = df[df['date'].isin(test_dates)].dropna(subset=feature_cols + [target_col])
        
        if train_df.empty or test_df.empty:
            continue
            
        X_train, y_train = train_df[feature_cols], train_df[target_col]
        X_test, y_test = test_df[feature_cols], test_df[target_col]
        
        model = model_factory()
        model.fit(X_train, y_train)
        
        # Store test_df alongside out-of-sample predictions
        test_pred_df = test_df[['ticker', 'date', 'log_return', target_col]].copy()
        test_pred_df['predicted_log_vol'] = model_factory.predict(X_test)
        oof_preds.append(test_pred_df)
    
    # Combines all test folds into single df
    return(pd.concat(oof_preds, ignore_index=True).sort_values(['ticker', 'date']).reset_index(drop=True))