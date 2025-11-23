# utils.py

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

def get_all_symbols() -> List[str]:
    """
    Get all symbols for data fetching
    """
    from config import STOCKS, ETFS, ICICI_SHUBH_NIVESH_STOCKS
    return list(set(STOCKS + ETFS + ICICI_SHUBH_NIVESH_STOCKS))

def print_execution_summary(stocks_stats: Dict, etfs_stats: Dict, icici_stats: Dict) -> None:
    """
    Print execution summary to console
    """
    total_buy = stocks_stats['buy_count'] + etfs_stats['buy_count'] + icici_stats['buy_count']
    total_sell = stocks_stats['sell_count'] + etfs_stats['sell_count'] + icici_stats['sell_count']
    
    print(f"\n=== Execution Summary ===")
    print(f"Total Buy Signals: {total_buy}")
    print(f"Total Sell Signals: {total_sell}")
    print(f"Stocks Analyzed: {stocks_stats['total_stocks']}")
    print(f"ETFs Analyzed: {etfs_stats['total_etfs']}")
    print(f"ICICI Stocks Analyzed: {icici_stats['total_stocks']}")
    print("=" * 30)