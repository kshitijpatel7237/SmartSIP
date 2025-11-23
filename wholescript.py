import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Configuration ---
st.set_page_config(
    page_title="Stock & ETF Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stock and ETF Lists
STOCKS = ['VMM.NS', 'MEDANTA.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'BALKRISIND.NS', 'MFSL.NS', 'HDFCBANK.NS',
          'ICICIBANK.NS', 'BLUESTARCO.NS']
ETFS = ['MAHKTECH.NS', 'MAFANG.NS', 'PHARMABEES.NS', 'NIFTYBEES.NS', 'GOLDBEES.NS', 'ICICIB22.NS', 'ITBEES.NS',
        'HDFCSML250.NS', 'PSUBANK.NS', 'AUTOBEES.NS', 'GROWWRAIL.NS', 'MODEFENCE.NS']
ICICI_SHUBH_NIVESH_STOCKS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                             'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS']

# Security Name Mappings
SECURITY_NAMES = {
    'BLUESTARCO.NS': 'Blue Star Co.',
    'VMM.NS': 'Vishal Mega Mart',
    'MEDANTA.NS': 'Medanta',
    'PERSISTENT.NS': 'Persistant System',
    'COFORGE.NS': 'Coforge',
    'BALKRISIND.NS': 'Balkrishna Industries',
    'MFSL.NS': 'Max Financial Service',
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank',
    'NIFTYBEES.NS': 'Nifty 50',
    'GOLDBEES.NS': 'Gold ETF',
    'SILVERBEES.NS': 'Silver ETF',
    'ITBEES.NS': 'Nifty IT ETF',
    'HDFCSML250.NS': 'SmallCap 150 Index Fund',
    'PSUBANK.NS': 'PSU Bank ETF',
    'AUTOBEES.NS': 'AUTO ETF',
    'GROWWRAIL.NS': 'Railway ETF',
    'MODEFENCE.NS': 'Defence ETF',
    'PHARMABEES.NS': 'Nippon Farma ETF',
    'MAFANG.NS': 'NYSE Fang ETF',
    'MAHKTECH.NS': 'Hang Seng Tech ETF'
}

ICICI_SECURITY_NAMES = {
    'RELIANCE.NS': 'Reliance Industries',
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank',
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'BHARTIARTL.NS': 'Bharti Airtel',
    'ITC.NS': 'ITC Limited',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'LT.NS': 'Larsen & Toubro'
}

# Investment Guidelines
STOCK_INVESTMENT_AMOUNT = "₹25,000"
ETF_INVESTMENT_AMOUNT = "₹50,000"


# --- Technical Indicator Functions ---
def pro_rsi(close, length=14):
    """Custom RSI calculation using EMA smoothing"""
    expo = 2 * length - 1
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    gcum = gain.ewm(span=expo, adjust=False).mean()
    lcum = loss.ewm(span=expo, adjust=False).mean()
    rs = gcum / lcum
    rsi = 100 - (100 / (1 + rs))
    return rsi.round(2)


def calculate_tsi(close, long=25, short=13, signal=13):
    """Calculate True Strength Index (TSI)"""
    momentum = close.diff()
    first_smooth = momentum.ewm(span=short, adjust=False).mean()
    second_smooth = first_smooth.ewm(span=long, adjust=False).mean()
    abs_momentum = abs(momentum)
    first_abs_smooth = abs_momentum.ewm(span=short, adjust=False).mean()
    second_abs_smooth = first_abs_smooth.ewm(span=long, adjust=False).mean()
    tsi = (second_smooth / second_abs_smooth) * 100
    signal_line = tsi.ewm(span=signal, adjust=False).mean()
    return tsi.round(4), signal_line.round(4)


def check_tsi_buy_signal(tsi_series, signal_series):
    """Check TSI buy signal"""
    if len(tsi_series) < 2 or len(signal_series) < 2:
        return False
    current_tsi = tsi_series.iloc[-1]
    current_signal = signal_series.iloc[-1]
    prev_tsi = tsi_series.iloc[-2]
    prev_signal = signal_series.iloc[-2]
    return (prev_tsi <= prev_signal) and (current_tsi > current_signal)


def check_tsi_sell_signal(tsi_series, signal_series):
    """Check TSI sell signal"""
    if len(tsi_series) < 2 or len(signal_series) < 2:
        return False
    current_tsi = tsi_series.iloc[-1]
    current_signal = signal_series.iloc[-1]
    prev_tsi = tsi_series.iloc[-2]
    prev_signal = signal_series.iloc[-2]
    return (prev_tsi >= prev_signal) and (current_tsi < current_signal)


def calculate_mfi_pandasta(high_prices, low_prices, close_prices, volumes, period=14):
    """Calculate MFI using pandas_ta"""
    return ta.mfi(high=high_prices, low=low_prices, close=close_prices, volume=volumes, length=period).round(2)


def calculate_ema(series, period):
    """Calculate Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def check_ema_crossover(ema9_series, ema26_series):
    """Check EMA crossover"""
    if len(ema9_series) < 2 or len(ema26_series) < 2:
        return False
    current_ema9 = ema9_series.iloc[-1]
    current_ema26 = ema26_series.iloc[-1]
    prev_ema9 = ema9_series.iloc[-2]
    prev_ema26 = ema26_series.iloc[-2]
    return (prev_ema9 > prev_ema26) and (current_ema9 <= current_ema26)


# --- Data Calculation Functions ---
def calculate_indicators_for_stocks(stock_list, data):
    """Calculate indicators for stocks"""
    rsi_data = pd.DataFrame(index=data.index)
    mfi_data = pd.DataFrame(index=data.index)
    ema_9_data = pd.DataFrame(index=data.index)
    ema_26_data = pd.DataFrame(index=data.index)

    for symbol in stock_list:
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 14:
                    rsi_data[symbol] = pro_rsi(close_trading, length=14)

        if all(col in data for col in ['High', 'Low', 'Close', 'Volume']) and symbol in data['High']:
            high_prices = data['High'][symbol]
            low_prices = data['Low'][symbol]
            close_prices = data['Close'][symbol]
            volumes = data['Volume'][symbol]
            trading_mask = volumes > 0
            high_trading = high_prices[trading_mask]
            low_trading = low_prices[trading_mask]
            close_trading = close_prices[trading_mask]
            volume_trading = volumes[trading_mask]
            if len(close_trading) > 14:
                mfi_data[symbol] = calculate_mfi_pandasta(high_trading, low_trading, close_trading, volume_trading)

        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 0:
                    ema_9_data[symbol] = calculate_ema(close_trading, period=9)
                    ema_26_data[symbol] = calculate_ema(close_trading, period=26)

    return rsi_data, mfi_data, ema_9_data, ema_26_data


def calculate_indicators_for_etfs(etf_list, data):
    """Calculate indicators for ETFs"""
    rsi_data = pd.DataFrame(index=data.index)
    mfi_data = pd.DataFrame(index=data.index)
    ema_9_data = pd.DataFrame(index=data.index)
    ema_26_data = pd.DataFrame(index=data.index)
    tsi_data = pd.DataFrame(index=data.index)
    tsi_signal_data = pd.DataFrame(index=data.index)

    for symbol in etf_list:
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 14:
                    rsi_data[symbol] = pro_rsi(close_trading, length=14)

        if all(col in data for col in ['High', 'Low', 'Close', 'Volume']) and symbol in data['High']:
            high_prices = data['High'][symbol]
            low_prices = data['Low'][symbol]
            close_prices = data['Close'][symbol]
            volumes = data['Volume'][symbol]
            trading_mask = volumes > 0
            high_trading = high_prices[trading_mask]
            low_trading = low_prices[trading_mask]
            close_trading = close_prices[trading_mask]
            volume_trading = volumes[trading_mask]
            if len(close_trading) > 14:
                mfi_data[symbol] = calculate_mfi_pandasta(high_trading, low_trading, close_trading, volume_trading)

        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 0:
                    ema_9_data[symbol] = calculate_ema(close_trading, period=9)
                    ema_26_data[symbol] = calculate_ema(close_trading, period=26)

        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 25:
                    tsi, tsi_signal = calculate_tsi(close_trading)
                    tsi_data[symbol] = tsi
                    tsi_signal_data[symbol] = tsi_signal

    return rsi_data, mfi_data, ema_9_data, ema_26_data, tsi_data, tsi_signal_data


# --- Analysis Functions ---
def analyze_stock_suggestions(stock_list, security_names_dict, rsi_data, mfi_data, ema_9_data, ema_26_data):
    """Analyze stocks and return suggestions"""
    suggestions_data = []
    for symbol in stock_list:
        security_name = security_names_dict.get(symbol, symbol)
        latest_rsi = 'N/A'
        latest_mfi = 'N/A'
        latest_ema9 = 'N/A'
        latest_ema26 = 'N/A'
        ema_cross_text = 'N/A'
        background_color = ''
        ema_diff_trend = 'N/A'
        ema_diff_bg_color = 'lightgrey'
        suggestion = 'Insufficient data'
        color_class = 'hold'
        ema_crossover_warning = False
        investment_warning = ''

        has_rsi_data = symbol in rsi_data.columns and not rsi_data[symbol].dropna().empty
        has_mfi_data = symbol in mfi_data.columns and not mfi_data[symbol].dropna().empty
        has_ema9_data = symbol in ema_9_data.columns and not ema_9_data[symbol].dropna().empty
        has_ema26_data = symbol in ema_26_data.columns and not ema_26_data[symbol].dropna().empty

        if has_rsi_data:
            latest_rsi = rsi_data[symbol].dropna().iloc[-1]
        if has_mfi_data:
            latest_mfi = mfi_data[symbol].dropna().iloc[-1]

        if has_ema9_data:
            ema9_series = ema_9_data[symbol].dropna()
            latest_ema9 = ema9_series.iloc[-1] if len(ema9_series) >= 1 else np.nan
            prev_ema9_4_days_ago = ema9_series.iloc[-5] if len(ema9_series) >= 5 else np.nan
        else:
            latest_ema9 = np.nan
            prev_ema9_4_days_ago = np.nan

        if has_ema26_data:
            ema26_series = ema_26_data[symbol].dropna()
            latest_ema26 = ema26_series.iloc[-1] if len(ema26_series) >= 1 else np.nan
            prev_ema26_4_days_ago = ema26_series.iloc[-5] if len(ema26_series) >= 5 else np.nan
        else:
            latest_ema26 = np.nan
            prev_ema26_4_days_ago = np.nan

        has_latest_ema9 = not pd.isna(latest_ema9)
        has_latest_ema26 = not pd.isna(latest_ema26)

        if has_latest_ema9 and has_latest_ema26:
            if latest_ema9 > latest_ema26:
                background_color = 'lightgreen'
                ema_cross_text = 'Above'
            else:
                background_color = 'lightcoral'
                ema_cross_text = 'Below'

            if has_ema9_data and has_ema26_data and len(ema9_series) >= 2 and len(ema26_series) >= 2:
                ema_crossover_warning = check_ema_crossover(ema9_series, ema26_series)

            if (has_latest_ema9 and has_latest_ema26 and
                    not pd.isna(prev_ema9_4_days_ago) and not pd.isna(prev_ema26_4_days_ago)):
                current_diff = abs(latest_ema9 - latest_ema26)
                prev_diff_4_days_ago = abs(prev_ema9_4_days_ago - prev_ema26_4_days_ago)
                if latest_ema9 < latest_ema26:
                    if current_diff < prev_diff_4_days_ago:
                        ema_diff_trend = 'Shortening'
                        ema_diff_bg_color = 'lightgreen'
                    elif current_diff > prev_diff_4_days_ago:
                        ema_diff_trend = 'Widening'
                        ema_diff_bg_color = 'lightcoral'
                elif latest_ema9 > latest_ema26:
                    if current_diff < prev_diff_4_days_ago:
                        ema_diff_trend = 'Shortening'
                        ema_diff_bg_color = 'lightgreen'
                    elif current_diff > prev_diff_4_days_ago:
                        ema_diff_trend = 'Widening'
                        ema_diff_bg_color = 'lightcoral'

        if has_rsi_data and has_mfi_data and has_latest_ema9 and has_latest_ema26:
            if ema_crossover_warning:
                color_class = 'sell'
                suggestion = 'Sell (EMA Crossover)'
            elif latest_rsi < 30 and latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
            elif latest_rsi < 30:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
            elif latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP (MFI)'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
            elif latest_rsi > 70 and latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down'
            elif latest_rsi > 70:
                color_class = 'sell'
                suggestion = 'Cut Down'
            elif latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down (MFI)'
            else:
                color_class = 'hold'
                suggestion = 'Hold'

        suggestions_data.append({
            'symbol': symbol,
            'security_name': security_name,
            'latest_rsi': latest_rsi,
            'latest_mfi': latest_mfi,
            'latest_ema9': latest_ema9,
            'latest_ema26': latest_ema26,
            'ema_cross_text': ema_cross_text,
            'background_color': background_color,
            'ema_diff_trend': ema_diff_trend,
            'ema_diff_bg_color': ema_diff_bg_color,
            'suggestion': suggestion,
            'color_class': color_class,
            'investment_warning': investment_warning,
            'ema_crossover_warning': ema_crossover_warning
        })

    return suggestions_data


def analyze_etf_suggestions(etf_list, security_names_dict, rsi_data, mfi_data, ema_9_data, ema_26_data, tsi_data,
                            tsi_signal_data):
    """Analyze ETFs and return suggestions"""
    suggestions_data = []
    for symbol in etf_list:
        security_name = security_names_dict.get(symbol, symbol)
        latest_rsi = 'N/A'
        latest_mfi = 'N/A'
        latest_ema9 = 'N/A'
        latest_ema26 = 'N/A'
        latest_tsi = 'N/A'
        latest_tsi_signal = 'N/A'
        min_rsi_4_days = 'N/A'
        max_rsi_4_days = 'N/A'
        ema_cross_text = 'N/A'
        background_color = ''
        tsi_signal_text = 'N/A'
        tsi_background_color = 'lightgrey'
        ema_diff_trend = 'N/A'
        ema_diff_bg_color = 'lightgrey'
        suggestion = 'Insufficient data'
        color_class = 'hold'
        ema_crossover_warning = False
        tsi_buy_signal = False
        tsi_sell_signal = False
        investment_warning = ''

        has_rsi_data = symbol in rsi_data.columns and not rsi_data[symbol].dropna().empty
        has_mfi_data = symbol in mfi_data.columns and not mfi_data[symbol].dropna().empty
        has_ema9_data = symbol in ema_9_data.columns and not ema_9_data[symbol].dropna().empty
        has_ema26_data = symbol in ema_26_data.columns and not ema_26_data[symbol].dropna().empty
        has_tsi_data = symbol in tsi_data.columns and not tsi_data[symbol].dropna().empty
        has_tsi_signal_data = symbol in tsi_signal_data.columns and not tsi_signal_data[symbol].dropna().empty

        if has_rsi_data:
            rsi_series = rsi_data[symbol].dropna()
            latest_rsi = rsi_series.iloc[-1] if len(rsi_series) >= 1 else np.nan
            if len(rsi_series) >= 4:
                last_4_rsi = rsi_series.iloc[-4:]
                min_rsi_4_days = last_4_rsi.min()
                max_rsi_4_days = last_4_rsi.max()

        if has_mfi_data:
            latest_mfi = mfi_data[symbol].dropna().iloc[-1]
        if has_tsi_data:
            latest_tsi = tsi_data[symbol].dropna().iloc[-1]
        if has_tsi_signal_data:
            latest_tsi_signal = tsi_signal_data[symbol].dropna().iloc[-1]

        if has_ema9_data:
            ema9_series = ema_9_data[symbol].dropna()
            latest_ema9 = ema9_series.iloc[-1] if len(ema9_series) >= 1 else np.nan
            prev_ema9_4_days_ago = ema9_series.iloc[-5] if len(ema9_series) >= 5 else np.nan
        else:
            latest_ema9 = np.nan
            prev_ema9_4_days_ago = np.nan

        if has_ema26_data:
            ema26_series = ema_26_data[symbol].dropna()
            latest_ema26 = ema26_series.iloc[-1] if len(ema26_series) >= 1 else np.nan
            prev_ema26_4_days_ago = ema26_series.iloc[-5] if len(ema26_series) >= 5 else np.nan
        else:
            latest_ema26 = np.nan
            prev_ema26_4_days_ago = np.nan

        has_latest_ema9 = not pd.isna(latest_ema9)
        has_latest_ema26 = not pd.isna(latest_ema26)
        has_latest_tsi = not pd.isna(latest_tsi)
        has_latest_tsi_signal = not pd.isna(latest_tsi_signal)

        if has_latest_ema9 and has_latest_ema26:
            if latest_ema9 > latest_ema26:
                background_color = 'lightgreen'
                ema_cross_text = 'Above'
            else:
                background_color = 'lightcoral'
                ema_cross_text = 'Below'

            if has_ema9_data and has_ema26_data and len(ema9_series) >= 2 and len(ema26_series) >= 2:
                ema_crossover_warning = check_ema_crossover(ema9_series, ema26_series)

            if (has_latest_ema9 and has_latest_ema26 and
                    not pd.isna(prev_ema9_4_days_ago) and not pd.isna(prev_ema26_4_days_ago)):
                current_diff = abs(latest_ema9 - latest_ema26)
                prev_diff_4_days_ago = abs(prev_ema9_4_days_ago - prev_ema26_4_days_ago)
                if latest_ema9 < latest_ema26:
                    if current_diff < prev_diff_4_days_ago:
                        ema_diff_trend = 'Shortening'
                        ema_diff_bg_color = 'lightgreen'
                    elif current_diff > prev_diff_4_days_ago:
                        ema_diff_trend = 'Widening'
                        ema_diff_bg_color = 'lightcoral'
                elif latest_ema9 > latest_ema26:
                    if current_diff < prev_diff_4_days_ago:
                        ema_diff_trend = 'Shortening'
                        ema_diff_bg_color = 'lightgreen'
                    elif current_diff > prev_diff_4_days_ago:
                        ema_diff_trend = 'Widening'
                        ema_diff_bg_color = 'lightcoral'

        if has_latest_tsi and has_latest_tsi_signal:
            if latest_tsi > latest_tsi_signal:
                tsi_background_color = 'lightgreen'
                tsi_signal_text = 'TSI > Signal'
            else:
                tsi_background_color = 'lightcoral'
                tsi_signal_text = 'TSI < Signal'

            if has_tsi_data and has_tsi_signal_data and len(tsi_data[symbol].dropna()) >= 2 and len(
                    tsi_signal_data[symbol].dropna()) >= 2:
                tsi_series = tsi_data[symbol].dropna()
                signal_series = tsi_signal_data[symbol].dropna()
                tsi_buy_signal = check_tsi_buy_signal(tsi_series, signal_series)
                tsi_sell_signal = check_tsi_sell_signal(tsi_series, signal_series)

        if has_rsi_data and has_mfi_data and has_latest_ema9 and has_latest_ema26 and has_latest_tsi and has_latest_tsi_signal:
            if tsi_buy_signal:
                color_class = 'buy'
                suggestion = 'Strong Buy (TSI Crossover)'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
            elif tsi_sell_signal:
                color_class = 'sell'
                suggestion = 'Sell (TSI Crossover)'
            elif ema_crossover_warning:
                color_class = 'sell'
                suggestion = 'Sell (EMA Crossover)'
            elif latest_rsi < 30 and latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
            elif latest_rsi < 30:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
            elif latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP (MFI)'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
            elif latest_rsi > 70 and latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down'
            elif latest_rsi > 70:
                color_class = 'sell'
                suggestion = 'Cut Down'
            elif latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down (MFI)'
            else:
                color_class = 'hold'
                suggestion = 'Hold'

        suggestions_data.append({
            'symbol': symbol,
            'security_name': security_name,
            'latest_rsi': latest_rsi,
            'latest_mfi': latest_mfi,
            'min_rsi_4_days': min_rsi_4_days,
            'max_rsi_4_days': max_rsi_4_days,
            'latest_ema9': latest_ema9,
            'latest_ema26': latest_ema26,
            'latest_tsi': latest_tsi,
            'latest_tsi_signal': latest_tsi_signal,
            'ema_cross_text': ema_cross_text,
            'tsi_signal_text': tsi_signal_text,
            'background_color': background_color,
            'tsi_background_color': tsi_background_color,
            'ema_diff_trend': ema_diff_trend,
            'ema_diff_bg_color': ema_diff_bg_color,
            'suggestion': suggestion,
            'color_class': color_class,
            'investment_warning': investment_warning,
            'ema_crossover_warning': ema_crossover_warning,
            'tsi_buy_signal': tsi_buy_signal,
            'tsi_sell_signal': tsi_sell_signal
        })

    return suggestions_data


# --- Streamlit UI ---
def main():
    st.title("📈 Stock & ETF Technical Analysis Dashboard")
    st.markdown("### Real-time Technical Analysis for Indian Stocks and ETFs")

    # Sidebar
    st.sidebar.title("Configuration")
    analysis_period = st.sidebar.selectbox(
        "Analysis Period",
        ["3mo", "6mo", "1y"],
        index=0
    )

    if st.sidebar.button("🔄 Refresh Analysis"):
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Investment Guidelines")
    st.sidebar.info(f"**Stocks:** {STOCK_INVESTMENT_AMOUNT} per buy signal")
    st.sidebar.info(f"**ETFs:** {ETF_INVESTMENT_AMOUNT} per buy signal")

    # Main content
    with st.spinner("Fetching market data and calculating indicators..."):
        try:
            # Fetch data
            all_symbols = list(set(STOCKS + ETFS + ICICI_SHUBH_NIVESH_STOCKS))
            data = yf.download(all_symbols, period=analysis_period, interval='1d', auto_adjust=True)

            # Calculate indicators
            stocks_rsi, stocks_mfi, stocks_ema9, stocks_ema26 = calculate_indicators_for_stocks(STOCKS, data)
            etfs_rsi, etfs_mfi, etfs_ema9, etfs_ema26, etfs_tsi, etfs_tsi_signal = calculate_indicators_for_etfs(ETFS,
                                                                                                                 data)
            icici_rsi, icici_mfi, icici_ema9, icici_ema26 = calculate_indicators_for_stocks(ICICI_SHUBH_NIVESH_STOCKS,
                                                                                            data)

            # Analyze suggestions
            stocks_suggestions = analyze_stock_suggestions(STOCKS, SECURITY_NAMES, stocks_rsi, stocks_mfi, stocks_ema9,
                                                           stocks_ema26)
            etfs_suggestions = analyze_etf_suggestions(ETFS, SECURITY_NAMES, etfs_rsi, etfs_mfi, etfs_ema9, etfs_ema26,
                                                       etfs_tsi, etfs_tsi_signal)
            icici_suggestions = analyze_stock_suggestions(ICICI_SHUBH_NIVESH_STOCKS, ICICI_SECURITY_NAMES, icici_rsi,
                                                          icici_mfi, icici_ema9, icici_ema26)

            # Summary Statistics
            st.success(
                f"✅ Successfully analyzed {len(stocks_suggestions) + len(etfs_suggestions) + len(icici_suggestions)} securities")

            # Summary Cards
            col1, col2, col3, col4 = st.columns(4)

            total_buy = len(
                [s for s in stocks_suggestions + etfs_suggestions + icici_suggestions if s['color_class'] == 'buy'])
            total_sell = len(
                [s for s in stocks_suggestions + etfs_suggestions + icici_suggestions if s['color_class'] == 'sell'])
            total_hold = len(
                [s for s in stocks_suggestions + etfs_suggestions + icici_suggestions if s['color_class'] == 'hold'])

            with col1:
                st.metric("Total Securities", len(stocks_suggestions) + len(etfs_suggestions) + len(icici_suggestions))
            with col2:
                st.metric("Buy Signals", total_buy, delta=f"+{total_buy}")
            with col3:
                st.metric("Sell Signals", total_sell, delta=f"-{total_sell}", delta_color="inverse")
            with col4:
                st.metric("Hold Signals", total_hold)

            # Stocks Portfolio
            st.markdown("---")
            st.header("📊 Stocks Portfolio")
            display_stock_table(stocks_suggestions)

            # ETFs Portfolio
            st.markdown("---")
            st.header("🏦 ETFs Portfolio (with TSI Analysis)")
            display_etf_table(etfs_suggestions)

            # ICICI Shubh Nivesh
            st.markdown("---")
            st.header("🏛️ ICICI Direct Shubh Nivesh (Strong Business Fundamentals)")
            display_stock_table(icici_suggestions)

            # Legend
            st.markdown("---")
            st.subheader("📖 Legend")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Signal Colors:**")
                st.markdown("- 🟢 **Buy**: RSI < 30 or MFI < 20")
                st.markdown("- 🔴 **Sell**: RSI > 70 or MFI > 80 or EMA Crossover")
                st.markdown("- 🟡 **Hold**: Neutral indicators")
            with col2:
                st.markdown("**EMA Status:**")
                st.markdown("- 🟢 **Above**: EMA9 > EMA26")
                st.markdown("- 🔴 **Below**: EMA9 < EMA26")
                st.markdown("- 📈 **Shortening**: Gap between EMAs is decreasing")
                st.markdown("- 📉 **Widening**: Gap between EMAs is increasing")
            with col3:
                st.markdown("**Special Indicators:**")
                st.markdown("- 🚀 **Strong Buy**: TSI crossover above signal line")
                st.markdown("- ⚠️ **Warning**: EMA crossover or TSI crossover below")
                st.markdown("- 💡 **Investment**: Recommended amount for buy signals")

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.info("Please check your internet connection and try again.")


def display_stock_table(suggestions_data):
    """Display stock analysis table"""
    if not suggestions_data:
        st.warning("No data available for stocks")
        return

    df_data = []
    for stock in suggestions_data:
        row = {
            'Security': stock['security_name'],
            'Symbol': stock['symbol'],
            'RSI': f"{stock['latest_rsi']:.2f}" if isinstance(stock['latest_rsi'], float) else stock['latest_rsi'],
            'MFI': f"{stock['latest_mfi']:.2f}" if isinstance(stock['latest_mfi'], float) else stock['latest_mfi'],
            'EMA9': f"{stock['latest_ema9']:.2f}" if isinstance(stock['latest_ema9'], float) else stock['latest_ema9'],
            'EMA26': f"{stock['latest_ema26']:.2f}" if isinstance(stock['latest_ema26'], float) else stock[
                'latest_ema26'],
            'EMA Cross': stock['ema_cross_text'],
            'EMA Trend': stock['ema_diff_trend'],
            'Suggestion': stock['suggestion'],
            'Investment': stock['investment_warning']
        }
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # Style the dataframe
    def color_suggestion(val):
        if 'Buy' in val:
            return 'background-color: #d4edda; color: #155724;'
        elif 'Sell' in val:
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return 'background-color: #fff3cd; color: #856404;'

    def color_ema_cross(val):
        if val == 'Above':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'Below':
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return ''

    def color_ema_trend(val):
        if val == 'Shortening':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'Widening':
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return ''

    styled_df = df.style.map(color_suggestion, subset=['Suggestion']) \
        .map(color_ema_cross, subset=['EMA Cross']) \
        .map(color_ema_trend, subset=['EMA Trend'])

    st.dataframe(styled_df, use_container_width=True, height=400)


def display_etf_table(suggestions_data):
    """Display ETF analysis table"""
    if not suggestions_data:
        st.warning("No data available for ETFs")
        return

    df_data = []
    for etf in suggestions_data:
        suggestion_display = etf['suggestion']
        if etf['tsi_buy_signal']:
            suggestion_display = f"🚀 {suggestion_display}"
        elif etf['tsi_sell_signal'] or etf['ema_crossover_warning']:
            suggestion_display = f"⚠️ {suggestion_display}"

        row = {
            'ETF': etf['security_name'],
            'Symbol': etf['symbol'],
            'RSI': f"{etf['latest_rsi']:.2f}" if isinstance(etf['latest_rsi'], float) else etf['latest_rsi'],
            'Min RSI (4d)': f"{etf['min_rsi_4_days']:.2f}" if isinstance(etf['min_rsi_4_days'], float) else etf[
                'min_rsi_4_days'],
            'Max RSI (4d)': f"{etf['max_rsi_4_days']:.2f}" if isinstance(etf['max_rsi_4_days'], float) else etf[
                'max_rsi_4_days'],
            'MFI': f"{etf['latest_mfi']:.2f}" if isinstance(etf['latest_mfi'], float) else etf['latest_mfi'],
            'EMA9': f"{etf['latest_ema9']:.2f}" if isinstance(etf['latest_ema9'], float) else etf['latest_ema9'],
            'EMA26': f"{etf['latest_ema26']:.2f}" if isinstance(etf['latest_ema26'], float) else etf['latest_ema26'],
            'EMA Cross': etf['ema_cross_text'],
            'EMA Trend': etf['ema_diff_trend'],
            'TSI': f"{etf['latest_tsi']:.4f}" if isinstance(etf['latest_tsi'], float) else etf['latest_tsi'],
            'TSI Signal': f"{etf['latest_tsi_signal']:.4f}" if isinstance(etf['latest_tsi_signal'], float) else etf[
                'latest_tsi_signal'],
            'TSI Status': etf['tsi_signal_text'],
            'Suggestion': suggestion_display,
            'Investment': etf['investment_warning']
        }
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # Style the dataframe
    def color_suggestion(val):
        if 'Buy' in val:
            return 'background-color: #d4edda; color: #155724;'
        elif 'Sell' in val:
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return 'background-color: #fff3cd; color: #856404;'

    def color_ema_cross(val):
        if val == 'Above':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'Below':
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return ''

    def color_ema_trend(val):
        if val == 'Shortening':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'Widening':
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return ''

    def color_tsi_status(val):
        if val == 'TSI > Signal':
            return 'background-color: #d4edda; color: #155724;'
        elif val == 'TSI < Signal':
            return 'background-color: #f8d7da; color: #721c24;'
        else:
            return ''

    styled_df = df.style.map(color_suggestion, subset=['Suggestion']) \
        .map(color_ema_cross, subset=['EMA Cross']) \
        .map(color_ema_trend, subset=['EMA Trend']) \
        .map(color_tsi_status, subset=['TSI Status'])

    st.dataframe(styled_df, use_container_width=True, height=400)


if __name__ == "__main__":
    main()