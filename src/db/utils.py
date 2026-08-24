import math
import pandas as pd

def clean_float(val):
    if val is None or pd.isna(val) or not math.isfinite(val):
        return None
    return float(val)


def build_result_rows(run_id: int, backtest_results_df, BacktestResult):
    return [
        BacktestResult(
            run_id=run_id,
            date=row["date"],
            ticker=row["ticker"],
            position=clean_float(row.get("position")),
            position_lagged=clean_float(row.get("position_lagged")),
            gross_return=clean_float(row.get("gross_return")),
            turnover=clean_float(row.get("turnover")),
            net_return=clean_float(row.get("net_return"))
        )
        for row in backtest_results_df.to_dict(orient="records")
    ]

def build_prediction_rows(run_id: int, predictions_df, target_col: str, Prediction):
    return [
        Prediction(
            run_id=run_id,
            date=row["date"],
            ticker=row["ticker"],
            target_value=clean_float(row.get(target_col)),
            predicted_value=clean_float(row.get("predicted_log_vol")),
            position=clean_float(row.get("position")),
        )
        for row in predictions_df.to_dict(orient="records")
    ]