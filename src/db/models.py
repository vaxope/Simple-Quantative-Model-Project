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
    volume = Column(Float)

class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_name = Column(String, nullable=False)
    status = Column(String, default="running")
    ticker = Column(String, nullable=True)
    model_name = Column(String, nullable=False)
    target_col = Column(String, nullable=False)
    cost_bps = Column(Float, nullable=False)
    
    # Dates & status messages
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    error_message = Column(String, nullable=True)

    # Calculated asynchronously upon completion
    sharpe = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    calmar = Column(Float, nullable=True)
    annualized_return = Column(Float, nullable=True)

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