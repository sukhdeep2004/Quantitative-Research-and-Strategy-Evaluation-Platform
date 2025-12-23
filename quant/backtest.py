from quant.data import fetch_price_data
from quant.risk import sharpe_ratio, max_drawdown
from quant.strategies import (
    moving_average_strategy,
    rsi_strategy,
    macd_strategy,
    bollinger_bands_strategy
)

def backtest(returns, signals):
    strategy_returns = signals.shift(1) * returns
    equity_curve = (1 + strategy_returns).cumprod()
    return equity_curve, strategy_returns
def run_all_backtests(ticker, start, end):
    """
    Runs backtests for 4 strategies and returns a model dictionary
    """

    df = fetch_price_data(ticker, start, end)

    returns = df['returns']

    backtest_models = {}


    ma_df = moving_average_strategy(df)
    equity, strat_returns = backtest(returns, ma_df['signal'])

    backtest_models['Moving Average'] = {
        'equity_curve': equity,
        'returns': strat_returns,
        'sharpe': sharpe_ratio(strat_returns),
        'max_drawdown': max_drawdown(equity)
    }


    rsi_df = rsi_strategy(df)
    equity, strat_returns = backtest(returns, rsi_df['signal'])

    backtest_models['RSI'] = {
        'equity_curve': equity,
        'returns': strat_returns,
        'sharpe': sharpe_ratio(strat_returns),
        'max_drawdown': max_drawdown(equity)
    }


    macd_df = macd_strategy(df)
    equity, strat_returns = backtest(returns, macd_df['signal'])

    backtest_models['MACD'] = {
        'equity_curve': equity,
        'returns': strat_returns,
        'sharpe': sharpe_ratio(strat_returns),
        'max_drawdown': max_drawdown(equity)
    }


    bb_df = bollinger_bands_strategy(df)
    equity, strat_returns = backtest(returns, bb_df['signal'])

    backtest_models['Bollinger Bands'] = {
        'equity_curve': equity,
        'returns': strat_returns,
        'sharpe': sharpe_ratio(strat_returns),
        'max_drawdown': max_drawdown(equity)
    }

    return backtest_models