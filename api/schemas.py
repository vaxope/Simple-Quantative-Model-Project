from datetime import date
from pydantic import BaseModel, ConfigDict

# Modified schemas from src/db/models.py but for pydantic
class PricePoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float

    model_config: ConfigDict(from_attributes=True)

class BacktestRunPoint(BaseModel):
    id: int
    run_name: str
    model_name: str
    target_col: str
    cost_bps: float
    start_date= date
    end_date: date
    sharpe: float
    max_drawdown: float
    calmar: float
    annualized_return: float

    model_config = ConfigDict(from_attributes=True)

class BacktestResultPoint(BaseModel):
    date: date
    position: float
    position_lagged: float
    gross_return: float
    turnover: float
    cost: float
    net_return: float

    model_config = ConfigDict(from_attributes=True)

class PredictionPoint(BaseModel):
    date: date
    target_value: float | None = None
    predicted_value: float
    position: float

    model_config = ConfigDict(from_attributes=True)
