from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import PredictionPoint
from src.db.models import Prediction
from src.db.session import get_db

router = APIRouter()

@router.get("/latest", response_model=list[PredictionPoint])
def get_latest_signals(db: Session = Depends(get_db)):
    # Fetch all predictions sorted by ticker and newest date first
    all_predictions = (
        db.query(Prediction)
        .order_by(Prediction.ticker, Prediction.date.desc())
        .all()
    )

    # Keep only the first (newest) record encountered for each ticker
    latest_per_ticker = {}
    for pred in all_predictions:
        if pred.ticker not in latest_per_ticker:
            latest_per_ticker[pred.ticker] = pred

    return list(latest_per_ticker.values())


# Dynamic path /{ticker} matches any ticker symbol
@router.get("/{ticker}", response_model=list[PredictionPoint])
def get_signals_by_ticker(
    ticker: str,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Prediction).filter(Prediction.ticker == ticker)

    if start:
        query = query.filter(Prediction.date >= start)
    if end:
        query = query.filter(Prediction.date <= end)

    return query.order_by(Prediction.date).all()