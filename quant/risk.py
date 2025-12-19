import numpy as np
from scipy.stats import norm

def sharpe_ratio(returns, rf=0):
    return (returns.mean() - rf) / returns.std() * np.sqrt(252)

def max_drawdown(equity):
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    return drawdown.min()

def value_at_risk(returns, alpha=0.05):
    return np.percentile(returns, 100 * alpha)

def expected_shortfall(returns, alpha=0.05):
    var = value_at_risk(returns, alpha)
    return returns[returns <= var].mean()
