import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

def moving_average_strategy(df, short_window=20, long_window=50):
    df = df.copy()

    df['MA_short'] = df['price'].rolling(short_window).mean()
    df['MA_long'] = df['price'].rolling(long_window).mean()

    df['signal'] = 0
    df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1
    df.loc[df['MA_short'] < df['MA_long'], 'signal'] = -1

    return df

def rsi_strategy(df, window=14, overbought=70, oversold=30):
    df = df.copy()
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['signal'] = 0
    df.loc[df['RSI'] > overbought, 'signal'] = -1
    df.loc[df['RSI'] < oversold, 'signal'] = 1

    return df

def macd_strategy(df, fast=12, slow=26, signal_window=9):
    df = df.copy()

    df['EMA_fast'] = df['price'].ewm(span=fast, adjust=False).mean()
    df['EMA_slow'] = df['price'].ewm(span=slow, adjust=False).mean()

    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['MACD_signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()

    df['signal'] = 0
    df.loc[df['MACD'] > df['MACD_signal'], 'signal'] = 1
    df.loc[df['MACD'] < df['MACD_signal'], 'signal'] = -1

    return df

def bollinger_bands_strategy(df, window=20, num_std=2):
    df = df.copy()

    df['MA'] = df['price'].rolling(window).mean()
    df['STD'] = df['price'].rolling(window).std()

    df['Upper_Band'] = df['MA'] + (df['STD'] * num_std)
    df['Lower_Band'] = df['MA'] - (df['STD'] * num_std)

    df['signal'] = 0
    df.loc[df['price'] > df['Upper_Band'], 'signal'] = -1
    df.loc[df['price'] < df['Lower_Band'], 'signal'] = 1

    return df

def cointegration_test(series1, series2):
    """Engle-Granger p-value; below 0.05 suggests the two price series are cointegrated"""
    _, pvalue, _ = coint(series1, series2)
    return pvalue

def _pair_positions(zscore, entry_z, exit_z):
    """Enter when the spread z-score passes entry_z and hold until it reverts inside exit_z"""
    position = 0
    positions = []
    for z in zscore:
        if np.isnan(z):
            position = 0
        elif position == 0 and z > entry_z:
            position = -1
        elif position == 0 and z < -entry_z:
            position = 1
        elif position == -1 and z < exit_z:
            position = 0
        elif position == 1 and z > -exit_z:
            position = 0
        positions.append(position)
    return pd.Series(positions, index=zscore.index)

def cointegration_strategy(df, pair_df, hedge_window=60, z_window=30, entry_z=2.0, exit_z=0.5):
    """
    Pairs trade on the spread price - hedge_ratio * pair_price.
    signal 1 is long df / short pair_df and -1 is the reverse; returns are spread returns per dollar held in df.
    """
    prices = pd.concat({'price': df['price'], 'pair_price': pair_df['price']}, axis=1, join='inner').dropna()
    if len(prices) < hedge_window + z_window:
        raise ValueError(
            f"Cointegration needs at least {hedge_window + z_window} overlapping trading days for both tickers"
        )

    price, pair_price = prices['price'], prices['pair_price']
    hedge_ratio = price.rolling(hedge_window).cov(pair_price) / pair_price.rolling(hedge_window).var()
    spread = price - hedge_ratio * pair_price
    zscore = (spread - spread.rolling(z_window).mean()) / spread.rolling(z_window).std()

    # hedge_ratio is shares of pair per share of df, so weight pair returns by its dollar value instead
    dollar_hedge = (hedge_ratio * pair_price / price).shift(1)
    prices['returns'] = (price.pct_change() - dollar_hedge * pair_price.pct_change()).fillna(0)
    prices['hedge_ratio'] = hedge_ratio
    prices['zscore'] = zscore
    prices['signal'] = _pair_positions(zscore, entry_z, exit_z)

    return prices