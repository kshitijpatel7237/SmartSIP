# analysis.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from indicators import calculate_ema, check_ema_crossover, check_tsi_buy_signal, check_tsi_sell_signal
from config import STOCK_INVESTMENT_AMOUNT, ETF_INVESTMENT_AMOUNT

def calculate_indicators_for_stocks(stock_list: List[str], data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calculate RSI, MFI, and EMAs for a given list of stocks
    """
    from indicators import pro_rsi, calculate_mfi_pandasta
    
    rsi_data = pd.DataFrame(index=data.index)
    mfi_data = pd.DataFrame(index=data.index)
    ema_9_data = pd.DataFrame(index=data.index)
    ema_26_data = pd.DataFrame(index=data.index)

    for symbol in stock_list:
        # RSI Calculation
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 14:
                    rsi_data[symbol] = pro_rsi(close_trading, length=14)

        # MFI Calculation
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

        # EMA Calculation
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

def calculate_indicators_for_etfs(etf_list: List[str], data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calculate RSI, MFI, EMAs, and TSI for ETFs
    """
    from indicators import pro_rsi, calculate_mfi_pandasta, calculate_tsi
    
    rsi_data = pd.DataFrame(index=data.index)
    mfi_data = pd.DataFrame(index=data.index)
    ema_9_data = pd.DataFrame(index=data.index)
    ema_26_data = pd.DataFrame(index=data.index)
    tsi_data = pd.DataFrame(index=data.index)
    tsi_signal_data = pd.DataFrame(index=data.index)

    for symbol in etf_list:
        # RSI Calculation
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 14:
                    rsi_data[symbol] = pro_rsi(close_trading, length=14)

        # MFI Calculation
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

        # EMA Calculation for standard analysis
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 0:
                    ema_9_data[symbol] = calculate_ema(close_trading, period=9)
                    ema_26_data[symbol] = calculate_ema(close_trading, period=26)

        # TSI Calculation for ETFs
        if symbol in data['Close']:
            close_prices = data['Close'][symbol]
            if symbol in data['Volume']:
                volume_data = data['Volume'][symbol]
                trading_mask = volume_data > 0
                close_trading = close_prices[trading_mask]
                if len(close_trading) > 25:  # Need enough data for TSI
                    tsi, tsi_signal = calculate_tsi(close_trading)
                    tsi_data[symbol] = tsi
                    tsi_signal_data[symbol] = tsi_signal

    return rsi_data, mfi_data, ema_9_data, ema_26_data, tsi_data, tsi_signal_data

def analyze_stock_suggestions(stock_list: List[str], security_names_dict: Dict[str, str], 
                             rsi_data: pd.DataFrame, mfi_data: pd.DataFrame, 
                             ema_9_data: pd.DataFrame, ema_26_data: pd.DataFrame) -> Tuple[List[Dict], Dict]:
    """
    Analyze stocks and return suggestions with statistics
    """
    suggestions_data = []
    buy_count = 0
    sell_count = 0
    hold_count = 0
    insufficient_data_count = 0

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

        # Check if data exists for this symbol
        has_rsi_data = symbol in rsi_data.columns and not rsi_data[symbol].dropna().empty
        has_mfi_data = symbol in mfi_data.columns and not mfi_data[symbol].dropna().empty
        has_ema9_data = symbol in ema_9_data.columns and not ema_9_data[symbol].dropna().empty
        has_ema26_data = symbol in ema_26_data.columns and not ema_26_data[symbol].dropna().empty

        if has_rsi_data:
            latest_rsi = rsi_data[symbol].dropna().iloc[-1]
        if has_mfi_data:
            latest_mfi = mfi_data[symbol].dropna().iloc[-1]

        # Retrieve latest and previous EMA values
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

        # Determine EMA Cross Status
        if has_latest_ema9 and has_latest_ema26:
            if latest_ema9 > latest_ema26:
                background_color = 'lightgreen'
                ema_cross_text = 'Above'
            else:
                background_color = 'lightcoral'
                ema_cross_text = 'Below'

            # Check for EMA crossover warning
            if has_ema9_data and has_ema26_data and len(ema9_series) >= 2 and len(ema26_series) >= 2:
                ema_crossover_warning = check_ema_crossover(ema9_series, ema26_series)

            # Calculate EMA Difference Trend
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

        # General suggestion logic
        if has_rsi_data and has_mfi_data and has_latest_ema9 and has_latest_ema26:
            # NEW LOGIC: If EMA crossover occurred (EMA9 was > EMA26 but now <= EMA26), suggest SELL
            if ema_crossover_warning:
                color_class = 'sell'
                suggestion = 'Sell (EMA Crossover)'
                sell_count += 1

            # Existing suggestion logic (only apply if no EMA crossover)
            elif latest_rsi < 30 and latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_rsi < 30:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP (MFI)'
                investment_warning = f'💡 Invest: {STOCK_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_rsi > 70 and latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down'
                sell_count += 1
            elif latest_rsi > 70:
                color_class = 'sell'
                suggestion = 'Cut Down'
                sell_count += 1
            elif latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down (MFI)'
                sell_count += 1
            else:
                color_class = 'hold'
                suggestion = 'Hold'
                hold_count += 1
        else:
            insufficient_data_count += 1

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

    statistics = {
        'total_stocks': len(stock_list),
        'buy_count': buy_count,
        'sell_count': sell_count,
        'hold_count': hold_count,
        'insufficient_data_count': insufficient_data_count
    }

    return suggestions_data, statistics

def analyze_etf_suggestions(etf_list: List[str], security_names_dict: Dict[str, str], 
                           rsi_data: pd.DataFrame, mfi_data: pd.DataFrame, 
                           ema_9_data: pd.DataFrame, ema_26_data: pd.DataFrame, 
                           tsi_data: pd.DataFrame, tsi_signal_data: pd.DataFrame) -> Tuple[List[Dict], Dict]:
    """
    Analyze ETFs and return suggestions with TSI logic
    """
    suggestions_data = []
    buy_count = 0
    sell_count = 0
    hold_count = 0
    insufficient_data_count = 0

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

        # Check if data exists for this symbol
        has_rsi_data = symbol in rsi_data.columns and not rsi_data[symbol].dropna().empty
        has_mfi_data = symbol in mfi_data.columns and not mfi_data[symbol].dropna().empty
        has_ema9_data = symbol in ema_9_data.columns and not ema_9_data[symbol].dropna().empty
        has_ema26_data = symbol in ema_26_data.columns and not ema_26_data[symbol].dropna().empty
        has_tsi_data = symbol in tsi_data.columns and not tsi_data[symbol].dropna().empty
        has_tsi_signal_data = symbol in tsi_signal_data.columns and not tsi_signal_data[symbol].dropna().empty

        if has_rsi_data:
            rsi_series = rsi_data[symbol].dropna()
            latest_rsi = rsi_series.iloc[-1] if len(rsi_series) >= 1 else np.nan
            
            # Calculate min and max RSI for last 4 days
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

        # Retrieve latest and previous EMA values for trend analysis
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

        # Determine EMA Cross Status
        if has_latest_ema9 and has_latest_ema26:
            if latest_ema9 > latest_ema26:
                background_color = 'lightgreen'
                ema_cross_text = 'Above'
            else:
                background_color = 'lightcoral'
                ema_cross_text = 'Below'

            # Check for EMA crossover warning
            if has_ema9_data and has_ema26_data and len(ema9_series) >= 2 and len(ema26_series) >= 2:
                ema_crossover_warning = check_ema_crossover(ema9_series, ema26_series)

            # Calculate EMA Difference Trend for ETFs
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

        # Determine TSI Signal Status
        if has_latest_tsi and has_latest_tsi_signal:
            if latest_tsi > latest_tsi_signal:
                tsi_background_color = 'lightgreen'
                tsi_signal_text = 'TSI > Signal'
            else:
                tsi_background_color = 'lightcoral'
                tsi_signal_text = 'TSI < Signal'

            # Check for TSI buy/sell signals
            if has_tsi_data and has_tsi_signal_data and len(tsi_data[symbol].dropna()) >= 2 and len(tsi_signal_data[symbol].dropna()) >= 2:
                tsi_series = tsi_data[symbol].dropna()
                signal_series = tsi_signal_data[symbol].dropna()
                tsi_buy_signal = check_tsi_buy_signal(tsi_series, signal_series)
                tsi_sell_signal = check_tsi_sell_signal(tsi_series, signal_series)

        # ETF Specific Suggestion Logic with TSI priority
        if has_rsi_data and has_mfi_data and has_latest_ema9 and has_latest_ema26 and has_latest_tsi and has_latest_tsi_signal:
            # Priority 1: TSI Buy Signal -> Strong Buy for ETFs
            if tsi_buy_signal:
                color_class = 'buy'
                suggestion = 'Strong Buy (TSI Crossover)'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
                buy_count += 1

            # Priority 2: TSI Sell Signal
            elif tsi_sell_signal:
                color_class = 'sell'
                suggestion = 'Sell (TSI Crossover)'
                sell_count += 1

            # Priority 3: Standard EMA Crossover Warning
            elif ema_crossover_warning:
                color_class = 'sell'
                suggestion = 'Sell (EMA Crossover)'
                sell_count += 1

            # Priority 4: Standard RSI/MFI logic
            elif latest_rsi < 30 and latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_rsi < 30:
                color_class = 'buy'
                suggestion = 'Make SIP'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_mfi < 20:
                color_class = 'buy'
                suggestion = 'Make SIP (MFI)'
                investment_warning = f'💡 Invest: {ETF_INVESTMENT_AMOUNT}'
                buy_count += 1
            elif latest_rsi > 70 and latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down'
                sell_count += 1
            elif latest_rsi > 70:
                color_class = 'sell'
                suggestion = 'Cut Down'
                sell_count += 1
            elif latest_mfi > 80:
                color_class = 'sell'
                suggestion = 'Cut Down (MFI)'
                sell_count += 1
            else:
                color_class = 'hold'
                suggestion = 'Hold'
                hold_count += 1
        else:
            insufficient_data_count += 1

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

    statistics = {
        'total_etfs': len(etf_list),
        'buy_count': buy_count,
        'sell_count': sell_count,
        'hold_count': hold_count,
        'insufficient_data_count': insufficient_data_count
    }

    return suggestions_data, statistics