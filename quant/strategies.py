import numpy as np

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