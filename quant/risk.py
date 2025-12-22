import numpy as np
from scipy.stats import norm

def sharpe_ratio(returns, rf=0):
    return (returns.mean() - rf) / returns.std() * np.sqrt(252)

def max_drawdown(equity):
    """Calculate maximum drawdown as a positive percentage"""
    peak = equity.cummax()
    drawdown = (peak - equity) / peak
    return drawdown.max()  # Returns positive value (e.g., 0.15 = 15% drawdown)

def value_at_risk(returns, alpha=0.05):
    return np.percentile(returns, 100 * alpha)

def expected_shortfall(returns, alpha=0.05):
    var = value_at_risk(returns, alpha)
    return returns[returns <= var].mean()

def compute_metrics(equity_curve, strategy_returns):
    """Compute key performance metrics"""
    final_equity = equity_curve.iloc[-1]
    total_return = (final_equity - 1) * 100

    # Calculate win rate correctly
    winning_trades = (strategy_returns > 0).sum()
    total_trades = (strategy_returns != 0).sum()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    num_trades = (strategy_returns != 0).sum()

    return final_equity, total_return, win_rate, num_trades