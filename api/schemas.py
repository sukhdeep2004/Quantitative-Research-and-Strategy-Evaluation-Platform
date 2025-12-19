from pydantic import BaseModel

class BacktestRequest(BaseModel):
    ticker: str
    start: str
    end: str
