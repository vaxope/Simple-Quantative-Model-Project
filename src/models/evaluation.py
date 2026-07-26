import numpy as np
import pandas as pd

import numpy as np
import pandas as pd

def evaluate_predictions(y_true: pd.Series, y_pred: pd.Series, baseline_for_direction: pd.Series = None,) -> pd.Series:
    y_true = pd.Series(y_true).reset_index(drop=True)
    y_pred = pd.Series(y_pred).reset_index(drop=True)

    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

    metrics = {"RMSE": rmse, "MAE": mae}

    if baseline_for_direction is not None:
        base = pd.Series(baseline_for_direction).reset_index(drop=True)
        actual_change = np.sign(y_true - base)
        pred_change = np.sign(y_pred - base)
        metrics["Directional_Accuracy"] = np.mean(actual_change == pred_change)

    return pd.Series(metrics)