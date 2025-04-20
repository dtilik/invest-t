"""
Helper functions for Tinkoff Invest trading bot
"""
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

def convert_candles_to_dataframe(candles):
    """Convert API candle response to pandas DataFrame"""
    candle_data = []
    for candle in candles:
        candle_data.append({
            "time": candle.time,
            "open": float(candle.open.units) + float(candle.open.nano) / 1e9,
            "high": float(candle.high.units) + float(candle.high.nano) / 1e9,
            "low": float(candle.low.units) + float(candle.low.nano) / 1e9,
            "close": float(candle.close.units) + float(candle.close.nano) / 1e9,
            "volume": candle.volume
        })
    
    return pd.DataFrame(candle_data)

def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """Calculate Moving Average Convergence Divergence"""
    exp1 = data.ewm(span=fast_period, adjust=False).mean()
    exp2 = data.ewm(span=slow_period, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    histogram = macd - signal
    
    return macd, signal, histogram

def calculate_bollinger_bands(data, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    ma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper_band = ma + (std * num_std)
    lower_band = ma - (std * num_std)
    
    return upper_band, ma, lower_band
