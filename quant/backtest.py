import numpy as np

def backtest(returns, signals):
    strategy_returns = signals.shift(1) * returns
    equity_curve = (1 + strategy_returns).cumprod()
    return equity_curve, strategy_returns
