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
            portfolio_return=clean_float(row.get("portfolio_return")),
            benchmark_return=clean_float(row.get("benchmark_return")),
            equity_curve=clean_float(row.get("equity_curve")),
        )
        for row in backtest_results_df.to_dict(orient="records")
    ]

def build_prediction_rows(run_id: int, predictions_df, target_col: str, Prediction):
    return [
        Prediction(
            run_id=run_id,
            date=row["date"],
            ticker=row["ticker"],
            target_value=clean_float(row.get("target_value")),
            predicted_value=clean_float(row.get("predicted_value")),
            position=clean_float(row.get("position")),
        )
        for row in predictions_df.to_dict(orient="records")
    ]