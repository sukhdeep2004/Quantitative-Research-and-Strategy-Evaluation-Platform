from quant.data import fetch_price_data
from quant.risk import compute_metrics
from quant.strategies import (
    moving_average_strategy,
    rsi_strategy,
    macd_strategy,
    bollinger_bands_strategy
)

STRATEGIES = {
    'Moving Average': (moving_average_strategy, {'short_window': 20, 'long_window': 50}),
    'RSI': (rsi_strategy, {'window': 14, 'overbought': 70, 'oversold': 30}),
    'MACD': (macd_strategy, {'fast': 12, 'slow': 26, 'signal_window': 9}),
    'Bollinger Bands': (bollinger_bands_strategy, {'window': 20, 'num_std': 2}),
}

def backtest(returns, signals):
    strategy_returns = signals.shift(1) * returns
    equity_curve = (1 + strategy_returns).cumprod()
    return equity_curve, strategy_returns

def run_strategy(df, strategy_name):
    """Backtest one named strategy from STRATEGIES on already-fetched price data"""
    strategy, params = STRATEGIES[strategy_name]
    signals = strategy(df, **params)['signal']
    equity, strat_returns = backtest(df['returns'], signals)

    return {
        'equity_curve': equity,
        'returns': strat_returns,
        'params': params,
        'metrics': compute_metrics(equity, strat_returns),
    }

def run_all_backtests(ticker, start, end):
    """
    Runs backtests for every strategy in STRATEGIES and returns a model dictionary
    """
    df = fetch_price_data(ticker, start, end)
    return {name: run_strategy(df, name) for name in STRATEGIES}
