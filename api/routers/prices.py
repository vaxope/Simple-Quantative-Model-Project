from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.models import Price
from api.schemas import PricePoint

router = APIRouter()

@router.get("/{ticker}", response_model=list[PricePoint])

# Takes ticker and optional start and end query params
# Gets db sesh, queries price table, and returns results ordered by date
def get_prices(
    ticker: str,
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    # Base query filtered by ticker
    query = db.query(Price).filter(Price.ticker == ticker)

    # Date filters if provided
    if start:
        query = query.filter(Price.date >= start)
    if end:
        query = query.filter(Price.date <= end)

    return query.order_by(Price.date).all()