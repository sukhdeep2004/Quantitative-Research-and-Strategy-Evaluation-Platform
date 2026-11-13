from quant.data import fetch_price_data
from quant.risk import compute_metrics
from quant.strategies import (
    moving_average_strategy,
    rsi_strategy,
    macd_strategy,
    bollinger_bands_strategy,
    cointegration_strategy,
    cointegration_test
)

STRATEGIES = {
    'Moving Average': (moving_average_strategy, {'short_window': 20, 'long_window': 50}),
    'RSI': (rsi_strategy, {'window': 14, 'overbought': 70, 'oversold': 30}),
    'MACD': (macd_strategy, {'fast': 12, 'slow': 26, 'signal_window': 9}),
    'Bollinger Bands': (bollinger_bands_strategy, {'window': 20, 'num_std': 2}),
}

COINTEGRATION_PARAMS = {'hedge_window': 60, 'z_window': 30, 'entry_z': 2.0, 'exit_z': 0.5}

def backtest(returns, signals):
    strategy_returns = signals.shift(1) * returns
    equity_curve = (1 + strategy_returns).cumprod()
    return equity_curve, strategy_returns

def _evaluate(strategy_output, params):
    equity, strat_returns = backtest(strategy_output['returns'], strategy_output['signal'])

    return {
        'equity_curve': equity,
        'returns': strat_returns,
        'params': params,
        'metrics': compute_metrics(equity, strat_returns),
    }

def run_strategy(df, strategy_name):
    """Backtest one named strategy from STRATEGIES on already-fetched price data"""
    strategy, params = STRATEGIES[strategy_name]
    return _evaluate(strategy(df, **params), params)

def run_cointegration(df, pair_df, pair_ticker):
    """Backtest the cointegration pairs strategy of df against pair_df"""
    output = cointegration_strategy(df, pair_df, **COINTEGRATION_PARAMS)
    run = _evaluate(output, COINTEGRATION_PARAMS)
    run['pair_ticker'] = pair_ticker.upper()
    run['coint_pvalue'] = round(float(cointegration_test(output['price'], output['pair_price'])), 4)
    return run

def run_all_backtests(ticker, start, end, pair_ticker=None):
    """
    Runs backtests for every strategy in STRATEGIES, plus cointegration against pair_ticker if given
    """
    df = fetch_price_data(ticker, start, end)
    results = {name: run_strategy(df, name) for name in STRATEGIES}

    if pair_ticker:
        pair_df = fetch_price_data(pair_ticker, start, end)
        results['Cointegration'] = run_cointegration(df, pair_df, pair_ticker)

    return results
