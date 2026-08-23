from datetime import date
from pydantic import BaseModel, ConfigDict

# Modified schemas from src/db/models.py but for pydantic
class PricePoint(BaseModel):
    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None

    model_config = ConfigDict(from_attributes=True)

class BacktestRunPoint(BaseModel):
    id: int
    run_name: str 
    model_name: str
    target_col: str
    cost_bps: float
    start_date: date
    end_date: date
    sharpe: float | None = None
    max_drawdown: float | None = None
    calmar: float | None = None
    annualized_return: float | None = None

    model_config = ConfigDict(from_attributes=True)

class BacktestResultPoint(BaseModel):
    date: date
    ticker: str
    position: float | None = None
    position_lagged: float | None = None
    gross_return: float | None = None
    turnover: float | None = None
    cost: float | None = None
    net_return: float | None = None

    model_config = ConfigDict(from_attributes=True)

class PredictionPoint(BaseModel):
    date: date
    ticker: str
    target_value: float | None = None
    predicted_value: float
    position: float

    model_config = ConfigDict(from_attributes=True)

class BacktestRunCreate(BaseModel):
    run_name: str
    tickers: list[str]
    model_name: str = "XGB"
    cost_bps: float = 5.0