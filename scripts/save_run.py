import math
import os
import pandas as pd
from datetime import datetime

from src.db.session import SessionLocal
from src.db.models import BacktestRun, BacktestResult, Prediction


def clean_float(val):
    if pd.isna(val) or not math.isfinite(val):
        return None
    return float(val)


def save_run(run_dir: str, model_name: str = None, target_col: str = "target_vol_5d", cost_bps: float = 10.0):
    session = SessionLocal()

    try:
        run_name = os.path.basename(os.path.normpath(run_dir))
        if model_name is None:
            model_name = run_name

        # Load run artifacts
        metrics_path = os.path.join(run_dir, "metrics.csv")
        predictions_path = os.path.join(run_dir, "predictions.parquet")
        results_path = os.path.join(run_dir, "backtest_results.parquet")

        metrics_df = pd.read_csv(metrics_path)
        
        # Flexibly parse metrics regardless of header names
        if "Metric" in metrics_df.columns and "Value" in metrics_df.columns:
            metrics = metrics_df.set_index("Metric")["Value"].to_dict()
        else:
            metrics = dict(zip(metrics_df.iloc[:, 0], metrics_df.iloc[:, 1]))

        predictions_df = pd.read_parquet(predictions_path)
        results_df = pd.read_parquet(results_path)

        # Extract date bounds
        start_date = pd.to_datetime(results_df["date"]).min().date()
        end_date = pd.to_datetime(results_df["date"]).max().date()

        # Parent BacktestRun record
        run = BacktestRun(
            run_name=run_name,
            model_name=model_name,
            target_col=target_col,
            cost_bps=cost_bps,
            start_date=start_date,
            end_date=end_date,
            sharpe=clean_float(metrics.get("Sharpe")),
            max_drawdown=clean_float(metrics.get("Max Drawdown")),
            calmar=clean_float(metrics.get("Calmar Ratio")),
            annualized_return=clean_float(metrics.get("Annualized Return")),
            created_at=datetime.now()
        )

        session.add(run)
        session.flush()

        # Child BacktestResult records
        results = [
            BacktestResult(
                run_id=run.id,
                ticker=row["ticker"],
                date=pd.to_datetime(row["date"]).date(),
                position=clean_float(row.get("position")),
                position_lagged=clean_float(row.get("position_lagged")),
                gross_return=clean_float(row.get("gross_return")),
                turnover=clean_float(row.get("turnover")),
                cost=clean_float(row.get("cost")),
                net_return=clean_float(row.get("net_return")),
            )
            for _, row in results_df.iterrows()
        ]

        # Child Prediction records
        predictions = [
            Prediction(
                run_id=run.id,
                ticker=row["ticker"],
                date=pd.to_datetime(row["date"]).date(),
                target_value=clean_float(row.get(target_col)),
                predicted_value=clean_float(row.get("predicted_log_vol")),
                position=clean_float(row.get("position")),
            )
            for _, row in predictions_df.iterrows()
        ]

        session.bulk_save_objects(results)
        session.bulk_save_objects(predictions)

        session.commit()
        print(f"Saved run '{run_name}' to DB (ID: {run.id})")

    except Exception as e:
        session.rollback()
        print(f"Error saving run: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    runs_dir = os.path.join("data", "runs")
    all_runs = [os.path.join(runs_dir, d) for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
    
    if all_runs:
        target_run = max(all_runs, key=os.path.getmtime)
        print(f"Loading latest run folder: {target_run}")
        save_run(target_run)
    else:
        print("No run directories found inside data/runs/")