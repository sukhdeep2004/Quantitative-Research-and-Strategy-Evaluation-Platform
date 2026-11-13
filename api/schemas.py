from datetime import date
from pydantic import BaseModel

class BacktestRequest(BaseModel):
    ticker: str
    start: date
    end: date
