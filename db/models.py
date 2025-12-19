from sqlalchemy import Column, Integer, Float, Date, String, DateTime
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MarketData(Base):
    __tablename__ = "market_data"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    price = Column(Float)
    returns = Column(Float)
class BacktestResult(Base):
    __tablename__ = "backtest_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    strategy_name = Column(String(100), default="Moving Average")
    sharpe_ratio = Column(Float)
    final_equity = Column(Float)
    max_drawdown = Column(Float)
    total_return = Column(Float)
    win_rate = Column(Float)
    num_trades = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)