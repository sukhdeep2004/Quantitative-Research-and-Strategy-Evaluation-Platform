import yfinance as yf
import pandas as pd

def fetch_price_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True)

    # ---- Robust price selection ----
    if 'Adj Close' in df.columns:
        price_col = 'Adj Close'
    elif 'Close' in df.columns:
        price_col = 'Close'
    else:
        raise ValueError(f"No price column found for {ticker}")

    df = df[[price_col, 'Volume']].copy()
    df.columns = ['price', 'volume']

    df.dropna(inplace=True)
    df['returns'] = df['price'].pct_change()

    return df.dropna()