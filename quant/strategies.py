from statsmodels.tsa.stattools import coint
import numpy as np

def cointegration_test(series1, series2):
    score, pvalue, _ = coint(series1, series2)
    return pvalue

def zscore_signal(spread, window=30):
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    z = (spread - mean) / std
    return z
def generate_signals(zscores, entry_threshold=2.0, exit_threshold=0.5):
    signals = np.where(zscores > entry_threshold, -1, 
                       np.where(zscores < -entry_threshold, 1, 0))
    exit_signals = np.where(np.abs(zscores) < exit_threshold, 0, signals)
    return exit_signals