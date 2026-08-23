from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import yaml
from src.db.session import get_db, SessionLocal
from src.db.models import BacktestRun
from api.schemas import BacktestRunCreate, BacktestRunPoint
from src.pipeline import run_full_pipeline
from src.db.utils import clean_float, build_prediction_rows, build_result_rows

router = APIRouter()

def run_and_save(run_id: int, tickers: list[str], model_name: str, cost_bps: float):
    db = SessionLocal()
    
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        config["data"]["tickers"] = tickers
        config["data"]["use_sp500"] = False
        config["model"]["name"] = model_name
        config["backtest"]["cost_bps"] = cost_bps

        results = run_full_pipeline(config)
        predictions_df = results["predictions"]
        backtest_results_df = results["backtest_results"]
        metrics = results["metrics"]

        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        run.sharpe = clean_float(metrics.get("Sharpe"))
        run.max_drawdown = clean_float(metrics.get("Max Drawdown"))
        run.calmar = clean_float(metrics.get("Calmar Ratio"))
        run.annualized_return = clean_float(metrics.get("Annualized Return"))
        run.status = "completed"

        db.bulk_save_objects(backtest_results_df)
        db.bulk_save_objects(predictions_df)
        db.commit()
    except Exception as e:
        db.rollback()
        run = db.query(BacktestRun).filter(BacktestRun.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/", response_model=BacktestRunPoint)
def create_backtest(
    payload: BacktestRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    pass

@router.get("/{run_id}", response_model=BacktestRunPoint)
def get_backtest(run_id: int, db: Session = Depends(get_db)):
    pass