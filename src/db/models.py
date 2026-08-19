from sqlalchemy import Column, String, Float, Date, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Price(Base):
    __tablename__ = "prices"

    ticker = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volumn = Column(Float)

class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    target_col = Column(String, nullable=False)
    cost_bps = Column(Float, nullable=False)
    start_date= Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    sharpe = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    calmar = Column(Float, nullable=False)
    annualized_return = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    position = Column(Float)
    position_lagged = Column(Float)
    gross_return = Column(Float)
    turnover = Column(Float)
    cost = Column(Float)
    net_return = Column(Float)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    target_value = Column(Float, nullable=True)
    predicted_value = Column(Float, nullable=False)
    position = Column(Float, nullable=False)