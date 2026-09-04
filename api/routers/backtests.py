from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import yaml
from src.db.session import get_db, SessionLocal
from src.db.models import BacktestRun, BacktestResult, Prediction
from src.pipeline import run_full_pipeline
from src.db.utils import clean_float, build_prediction_rows, build_result_rows
from api.schemas import BacktestRunCreate, BacktestRunPoint, BacktestResultPoint
from datetime import date
import pandas as pd

router = APIRouter()

# Runs model pipeline in background tasks and persists metrics, prediction rows, and results into PostgreSQL
def run_and_save(run_id: int, tickers: list[str], model_name: str, cost_bps: float):
    db = SessionLocal()
    
    try:
        # Load config as a base and dynamically override parameters based on user input
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        config["data"]["tickers"] = tickers
        config["data"]["use_sp500"] = False
        config["model"]["name"] = model_name
        config["data"]["force_download"] = True  # Forces fresh yfinance download for dynamic tickers
        config["backtest"]["cost_bps"] = cost_bps

        # Execute model pipeline
        results = run_full_pipeline(config)
        predictions_df = results["predictions"]
        backtest_results_df = results["backtest_results"]
        metrics = results["metrics"]

        # Infer target col name so pred df fields map correctly regardless of horizon set
        horizon = config["target"]["horizons"][0]
        target_vol = f"target_vol_{horizon}d"

        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()

        if not backtest_results_df.empty and "date" in backtest_results_df.columns:
            run.start_date = pd.to_datetime(backtest_results_df["date"].min()).date()
            run.end_date = pd.to_datetime(backtest_results_df["date"].max()).date()

        # Convert pandas Series to dict if necessary
        if isinstance(metrics, (pd.Series, pd.DataFrame)):
            metrics_dict = metrics.to_dict()
        else:
            metrics_dict = metrics

        # Log for easy debugging in terminal
        print(f"[DEBUG] Extracted metrics dict: {metrics_dict}")

        # Extract values using exact index keys from compute_backtest_metrics
        run.sharpe = clean_float(metrics_dict.get("Sharpe") or metrics_dict.get("sharpe"))
        run.max_drawdown = clean_float(metrics_dict.get("Max Drawdown") or metrics_dict.get("max_drawdown"))
        run.calmar = clean_float(metrics_dict.get("Calmar Ratio") or metrics_dict.get("calmar") or metrics_dict.get("calmar_ratio"))
        run.annualized_return = clean_float(metrics_dict.get("Annualized Return") or metrics_dict.get("annualized_return"))
        run.status = "completed"

        # Transform dfs into SQLAlchemy model instances
        result_rows = build_result_rows(run_id, backtest_results_df, BacktestResult)
        prediction_rows = build_prediction_rows(run_id, predictions_df, target_vol, Prediction)

        # Bulk insert row collectiosn into DB for efficiency
        db.bulk_save_objects(result_rows)
        db.bulk_save_objects(prediction_rows)
        db.commit()
    except Exception as e:
        # Rollback and re-query clean transaction to persist failure status and exeception message
        db.rollback()
        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            db.commit()
    finally:
        db.close()

# Post endpoint to initialize a new backtest run reocrd and delegate processing to fastapi background task executor
@router.post("/", response_model=BacktestRunPoint)
def create_backtest(
    payload: BacktestRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Determine target_vol default from config before async launch
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    horizon = config["target"]["horizons"][0]
    
    # Build backtestrun row from payload
    run = BacktestRun(
        run_name=getattr(payload, "run_name", f"{payload.model_name}_run"),
        status="running",
        ticker=",".join(payload.tickers),
        model_name=payload.model_name,
        cost_bps=payload.cost_bps,
        target_col=f"target_vol_{horizon}d",
    )

    # Persist parent run to database so run.id is generated before async launch
    db.add(run)
    db.commit()
    db.refresh(run)

    # Queue execution task to process async in background thread
    background_tasks.add_task(run_and_save, run.id, payload.tickers, payload.model_name, payload.cost_bps)

    return run

# gets backtests
@router.get("/{run_id}", response_model=BacktestRunPoint)
def get_backtest(run_id: int, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Backtest run {run_id} not found")
    return run

# Gets backtests results filtered by run_id ordered by date
@router.get("/{run_id}/results", response_model=list[BacktestResultPoint])
def get_backtests_results(run_id: int, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail=f"Backtest run {run_id} not found")
    
    results = (
        db.query(BacktestResult)
        .filter(BacktestResult.run_id == run_id)
        .order_by(BacktestResult.date.asc())
        .all()
    )

    return results