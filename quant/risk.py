import numpy as np

def sharpe_ratio(returns, rf=0):
    return (returns.mean() - rf) / returns.std() * np.sqrt(252)

def max_drawdown(equity):
    """Calculate maximum drawdown as a positive percentage"""
    peak = equity.cummax()
    drawdown = (peak - equity) / peak
    return drawdown.max()

def value_at_risk(returns, alpha=0.05):
    return np.percentile(returns, 100 * alpha)

def expected_shortfall(returns, alpha=0.05):
    var = value_at_risk(returns, alpha)
    return returns[returns <= var].mean()

def compute_metrics(equity_curve, strategy_returns):
    """Compute key performance metrics. max_drawdown, total_return and win_rate are percentages."""
    final_equity = equity_curve.iloc[-1]
    total_return = (final_equity - 1) * 100

    winning_trades = (strategy_returns > 0).sum()
    total_trades = (strategy_returns != 0).sum()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    return {
        'sharpe_ratio': round(float(sharpe_ratio(strategy_returns)), 3),
        'final_equity': round(float(final_equity), 4),
        'max_drawdown': round(float(max_drawdown(equity_curve)) * 100, 2),
        'total_return': round(float(total_return), 2),
        'win_rate': round(float(win_rate), 2),
        'num_trades': int(total_trades),
    }