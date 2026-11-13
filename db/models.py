import json
from sqlalchemy import Column, Integer, Float, Date, String, DateTime
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

from quant.version import CODE_VERSION

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
    pair_ticker = Column(String(10))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    strategy_name = Column(String(100), default="Moving Average")
    sharpe_ratio = Column(Float)
    final_equity = Column(Float)
    max_drawdown = Column(Float)
    total_return = Column(Float)
    win_rate = Column(Float)
    num_trades = Column(Integer)
    parameters = Column(String(500))
    code_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def from_run(cls, ticker, start_date, end_date, strategy_name, run):
        """Build a row from one entry returned by quant.backtest.run_strategy or run_cointegration"""
        return cls(
            ticker=ticker.upper(),
            pair_ticker=run.get('pair_ticker'),
            start_date=start_date,
            end_date=end_date,
            strategy_name=strategy_name,
            parameters=json.dumps(run['params'], sort_keys=True),
            code_version=CODE_VERSION,
            **run['metrics'],
        )
