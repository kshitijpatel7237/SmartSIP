# indicators.py

import pandas as pd
import numpy as np
import pandaps_ta as ta
from typing import Tuple

def pro_rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """
    Custom RSI calculation using EMA smoothing (matches Pine Script approach)
    """
    expo = 2 * length - 1  # Same as Pine Script: expo = 2*rsiLength - 1

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # EMA smoothing with period = expo
    gcum = gain.ewm(span=expo, adjust=False).mean()
    lcum = loss.ewm(span=expo, adjust=False).mean()

    rs = gcum / lcum
    rsi = 100 - (100 / (1 + rs))

    return rsi.round(2)

def calculate_tsi(close: pd.Series, long: int = 25, short: int = 13, signal: int = 13) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate True Strength Index (TSI)
    """
    # Calculate momentum
    momentum = close.diff()

    # First smoothing: EMA with short period
    first_smooth = momentum.ewm(span=short, adjust=False).mean()

    # Second smoothing: EMA with long period
    second_smooth = first_smooth.ewm(span=long, adjust=False).mean()

    # Calculate absolute momentum
    abs_momentum = abs(momentum)
    first_abs_smooth = abs_momentum.ewm(span=short, adjust=False).mean()
    second_abs_smooth = first_abs_smooth.ewm(span=long, adjust=False).mean()

    # Calculate TSI
    tsi = (second_smooth / second_abs_smooth) * 100

    # Signal line
    signal_line = tsi.ewm(span=signal, adjust=False).mean()

    return tsi.round(4), signal_line.round(4)

def check_tsi_buy_signal(tsi_series: pd.Series, signal_series: pd.Series) -> bool:
    """
    Check TSI buy signal: TSI crosses above signal line from below
    """
    if len(tsi_series) < 2 or len(signal_series) < 2:
        return False

    # Get current and previous values
    current_tsi = tsi_series.iloc[-1]
    current_signal = signal_series.iloc[-1]
    prev_tsi = tsi_series.iloc[-2]
    prev_signal = signal_series.iloc[-2]

    # Buy signal: TSI was below signal line but now crosses above
    buy_signal = (prev_tsi <= prev_signal) and (current_tsi > current_signal)

    return buy_signal

def check_tsi_sell_signal(tsi_series: pd.Series, signal_series: pd.Series) -> bool:
    """
    Check TSI sell signal: TSI crosses below signal line from above
    """
    if len(tsi_series) < 2 or len(signal_series) < 2:
        return False

    # Get current and previous values
    current_tsi = tsi_series.iloc[-1]
    current_signal = signal_series.iloc[-1]
    prev_tsi = tsi_series.iloc[-2]
    prev_signal = signal_series.iloc[-2]

    # Sell signal: TSI was above signal line but now crosses below
    sell_signal = (prev_tsi >= prev_signal) and (current_tsi < current_signal)

    return sell_signal

def calculate_mfi_pandasta(high_prices: pd.Series, low_prices: pd.Series, 
                          close_prices: pd.Series, volumes: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate MFI using pandas_ta library
    """
    return ta.mfi(high=high_prices, low=low_prices, close=close_prices, volume=volumes, length=period).round(2)

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculates the Exponential Moving Average (EMA) for a given pandas Series.
    """
    return series.ewm(span=period, adjust=False).mean()

def check_ema_crossover(ema9_series: pd.Series, ema26_series: pd.Series) -> bool:
    """
    Check if EMA9 was above EMA26 on previous day but now EMA9 <= EMA26
    """
    if len(ema9_series) < 2 or len(ema26_series) < 2:
        return False

    # Get current and previous day values
    current_ema9 = ema9_series.iloc[-1]
    current_ema26 = ema26_series.iloc[-1]
    prev_ema9 = ema9_series.iloc[-2]
    prev_ema26 = ema26_series.iloc[-2]

    # Check condition: previous day EMA9 > EMA26 AND current day EMA9 <= EMA26
    crossover_occurred = (prev_ema9 > prev_ema26) and (current_ema9 <= current_ema26)

    return crossover_occurred