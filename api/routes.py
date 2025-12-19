from fastapi import APIRouter
from quant.data import fetch_price_data
from quant.backtest import backtest
from quant.risk import sharpe_ratio

router = APIRouter()

@router.post("/run-backtest")
def run_backtest(req: dict):
    df = fetch_price_data(req["ticker"], req["start"], req["end"])
    signals = df['returns'].rolling(20).mean().apply(lambda x: -1 if x > 0 else 1)
    equity, strat_returns = backtest(df['returns'], signals)

    return {
        "sharpe": sharpe_ratio(strat_returns),
        "final_equity": float(equity.iloc[-1])
    }
