import yfinance as yf
import pandas as pd

def fetch_price_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end,auto_adjust=False)
    df = df[['Adj Close', 'Volume']]
    df.columns = ['price', 'volume']
    df.dropna(inplace=True)
    df['returns'] = df['price'].pct_change()
    return df.dropna()
