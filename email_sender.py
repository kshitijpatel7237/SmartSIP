# email_sender.py

import smtplib
from email.message import EmailMessage
from typing import Dict, List

def generate_summary_html(stocks_stats: Dict, etfs_stats: Dict, icici_stats: Dict) -> str:
    """
    Generate summary HTML with trade package statistics
    """
    from config import STOCK_INVESTMENT_AMOUNT, ETF_INVESTMENT_AMOUNT
    
    total_buy = stocks_stats['buy_count'] + etfs_stats['buy_count'] + icici_stats['buy_count']
    total_sell = stocks_stats['sell_count'] + etfs_stats['sell_count'] + icici_stats['sell_count']
    total_hold = stocks_stats['hold_count'] + etfs_stats['hold_count'] + icici_stats['hold_count']
    total_securities = stocks_stats['total_stocks'] + etfs_stats['total_etfs'] + icici_stats['total_stocks']

    summary_html = f'''
    <div class="summary-section">
        <h3>📊 Trade Package Summary (Kshitij)</h3>
        <div class="summary-stats">
            <div class="stat-card total">
                <h4>Total Securities</h4>
                <div class="stat-number">{total_securities}</div>
            </div>
            <div class="stat-card buy">
                <h4>Buy Signals</h4>
                <div class="stat-number">{total_buy}</div>
            </div>
            <div class="stat-card sell">
                <h4>Sell Signals</h4>
                <div class="stat-number">{total_sell}</div>
            </div>
            <div class="stat-card hold">
                <h4>Hold Signals</h4>
                <div class="stat-number">{total_hold}</div>
            </div>
        </div>
        <div class="portfolio-breakdown">
            <div class="portfolio-main">
                <h4>Stocks</h4>
                <p>Buy: {stocks_stats['buy_count']} | Sell: {stocks_stats['sell_count']} | Hold: {stocks_stats['hold_count']} | Total: {stocks_stats['total_stocks']}</p>
            </div>
            <div class="portfolio-etfs">
                <h4>ETFs</h4>
                <p>Buy: {etfs_stats['buy_count']} | Sell: {etfs_stats['sell_count']} | Hold: {etfs_stats['hold_count']} | Total: {etfs_stats['total_etfs']}</p>
            </div>
            <div class="portfolio-icici">
                <h4>ICICI Shubh Nivesh</h4>
                <p>Buy: {icici_stats['buy_count']} | Sell: {icici_stats['sell_count']} | Hold: {icici_stats['hold_count']} | Total: {icici_stats['total_stocks']}</p>
            </div>
        </div>
        <div class="investment-guidelines">
            <h4>💰 Investment Guidelines</h4>
            <p><strong>Stocks:</strong> Invest {STOCK_INVESTMENT_AMOUNT} per buy signal</p>
            <p><strong>ETFs:</strong> Invest {ETF_INVESTMENT_AMOUNT} per buy signal</p>
        </div>
    </div>
    '''
    return summary_html

def generate_stock_table_html(suggestions_data: List[Dict], section_title: str) -> str:
    """
    Generate HTML table for stocks
    """
    html_content = f'''
    <h3>{section_title}</h3>
    <table>
        <tr>
            <th>Security Name</th>
            <th>Symbol</th>
            <th>Latest RSI</th>
            <th>Latest MFI</th>
            <th>EMA (9)</th>
            <th>EMA (26)</th>
            <th>EMA Cross Status</th>
            <th>EMA Diff Trend</th>
            <th>Suggestion</th>
            <th>Investment</th>
        </tr>
'''

    for stock_data in suggestions_data:
        # Add warning icon if EMA crossover detected
        suggestion_display = stock_data['suggestion']
        if stock_data['ema_crossover_warning']:
            suggestion_display = f"⚠️ {suggestion_display}"

        html_content += f'''
        <tr>
            <td>{stock_data['security_name']}</td>
            <td>{stock_data['symbol']}</td>
            <td class="{stock_data['color_class']}">{f"{stock_data['latest_rsi']:.2f}" if isinstance(stock_data['latest_rsi'], float) else stock_data['latest_rsi']}</td>
            <td class="{stock_data['color_class']}">{f"{stock_data['latest_mfi']:.2f}" if isinstance(stock_data['latest_mfi'], float) else stock_data['latest_mfi']}</td>
            <td>{f"{stock_data['latest_ema9']:.2f}" if isinstance(stock_data['latest_ema9'], float) else stock_data['latest_ema9']}</td>
            <td>{f"{stock_data['latest_ema26']:.2f}" if isinstance(stock_data['latest_ema26'], float) else stock_data['latest_ema26']}</td>
            <td style="background-color: {stock_data['background_color']};">{stock_data['ema_cross_text']}</td>
            <td style="background-color: {stock_data['ema_diff_bg_color']};">{stock_data['ema_diff_trend']}</td>
            <td>{suggestion_display}</td>
            <td style="font-weight: bold;">{stock_data['investment_warning']}</td>
        </tr>
'''

    html_content += '''
    </table>
'''
    return html_content

def generate_etf_table_html(suggestions_data: List[Dict], section_title: str) -> str:
    """
    Generate HTML table for ETFs with TSI information
    """
    html_content = f'''
    <h3>{section_title}</h3>
    <table>
        <tr>
            <th>ETF Name</th>
            <th>Symbol</th>
            <th>Latest RSI</th>
            <th>Min RSI (4d)</th>
            <th>Max RSI (4d)</th>
            <th>Latest MFI</th>
            <th>EMA (9)</th>
            <th>EMA (26)</th>
            <th>EMA Cross Status</th>
            <th>EMA Diff Trend</th>
            <th>TSI</th>
            <th>TSI Signal</th>
            <th>TSI Status</th>
            <th>Suggestion</th>
            <th>Investment</th>
        </tr>
'''

    for etf_data in suggestions_data:
        # Add special icons for TSI signals
        suggestion_display = etf_data['suggestion']
        if etf_data['tsi_buy_signal']:
            suggestion_display = f"🚀 {suggestion_display}"
        elif etf_data['tsi_sell_signal']:
            suggestion_display = f"⚠️ {suggestion_display}"
        elif etf_data['ema_crossover_warning']:
            suggestion_display = f"⚠️ {suggestion_display}"

        # Color code for min and max RSI
        min_rsi_class = ''
        max_rsi_class = ''
        if isinstance(etf_data['min_rsi_4_days'], float):
            if etf_data['min_rsi_4_days'] < 30:
                min_rsi_class = 'buy'
            elif etf_data['min_rsi_4_days'] > 70:
                min_rsi_class = 'sell'
        
        if isinstance(etf_data['max_rsi_4_days'], float):
            if etf_data['max_rsi_4_days'] < 30:
                max_rsi_class = 'buy'
            elif etf_data['max_rsi_4_days'] > 70:
                max_rsi_class = 'sell'

        html_content += f'''
        <tr>
            <td>{etf_data['security_name']}</td>
            <td>{etf_data['symbol']}</td>
            <td class="{etf_data['color_class']}">{f"{etf_data['latest_rsi']:.2f}" if isinstance(etf_data['latest_rsi'], float) else etf_data['latest_rsi']}</td>
            <td class="{min_rsi_class}">{f"{etf_data['min_rsi_4_days']:.2f}" if isinstance(etf_data['min_rsi_4_days'], float) else etf_data['min_rsi_4_days']}</td>
            <td class="{max_rsi_class}">{f"{etf_data['max_rsi_4_days']:.2f}" if isinstance(etf_data['max_rsi_4_days'], float) else etf_data['max_rsi_4_days']}</td>
            <td class="{etf_data['color_class']}">{f"{etf_data['latest_mfi']:.2f}" if isinstance(etf_data['latest_mfi'], float) else etf_data['latest_mfi']}</td>
            <td>{f"{etf_data['latest_ema9']:.2f}" if isinstance(etf_data['latest_ema9'], float) else etf_data['latest_ema9']}</td>
            <td>{f"{etf_data['latest_ema26']:.2f}" if isinstance(etf_data['latest_ema26'], float) else etf_data['latest_ema26']}</td>
            <td style="background-color: {etf_data['background_color']};">{etf_data['ema_cross_text']}</td>
            <td style="background-color: {etf_data['ema_diff_bg_color']};">{etf_data['ema_diff_trend']}</td>
            <td>{f"{etf_data['latest_tsi']:.4f}" if isinstance(etf_data['latest_tsi'], float) else etf_data['latest_tsi']}</td>
            <td>{f"{etf_data['latest_tsi_signal']:.4f}" if isinstance(etf_data['latest_tsi_signal'], float) else etf_data['latest_tsi_signal']}</td>
            <td style="background-color: {etf_data['tsi_background_color']};">{etf_data['tsi_signal_text']}</td>
            <td>{suggestion_display}</td>
            <td style="font-weight: bold;">{etf_data['investment_warning']}</td>
        </tr>
'''

    html_content += '''
    </table>
'''
    return html_content

def send_email(stocks_suggestions: List[Dict], etfs_suggestions: List[Dict], icici_suggestions: List[Dict],
              stocks_stats: Dict, etfs_stats: Dict, icici_stats: Dict) -> None:
    """
    Send the analysis report via email
    """
    from config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, STOCK_INVESTMENT_AMOUNT, ETF_INVESTMENT_AMOUNT
    
    # Prepare HTML email content
    email_body_html = '''
<html>
<head>
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 20px;
        background-color: #f4f4f4;
        color: #333;
    }
    h2 {
        color: #0056b3;
        text-align: center;
        margin-bottom: 25px;
    }
    h3 {
        color: #28a745;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 2px solid #28a745;
    }
    h4 {
        color: #495057;
        margin-bottom: 10px;
    }
    p {
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .summary-section {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .summary-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .stat-card {
        flex: 1;
        min-width: 120px;
        background: white;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border-left: 4px solid #6c757d;
    }
    .stat-card.total { border-left-color: #0056b3; }
    .stat-card.buy { border-left-color: #28a745; }
    .stat-card.sell { border-left-color: #dc3545; }
    .stat-card.hold { border-left-color: #ffc107; }
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .portfolio-breakdown {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    .portfolio-main, .portfolio-etfs, .portfolio-icici {
        flex: 1;
        min-width: 200px;
        background: #f8f9fa;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
        border-left: 4px solid #0056b3;
    }
    .portfolio-etfs {
        border-left-color: #17a2b8;
    }
    .portfolio-icici {
        border-left-color: #28a745;
    }
    .investment-guidelines {
        background: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        border-left: 4px solid #0056b3;
    }
    table {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-collapse: collapse;
        width: 100%;
        margin-top: 20px;
        border: 1px solid #cccccc;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    th, td {
        border-bottom: 1px solid #e0e0e0;
        padding: 6px 8px;
        vertical-align: middle;
        font-size: 0.85em;
    }
    th {
        background-color: #d9d9d9;
        color: #222;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #bbbbbb;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    td:first-child {
        text-align: left;
    }
    td:nth-child(n+2) {
        text-align: center;
    }
    .buy { color: #28a745; font-weight: bold; }
    .sell { color: #dc3545; font-weight: bold; }
    .hold { color: #ffc107; font-weight: bold; }
    i {
        color: #6c757d;
    }
    .footer-text {
        font-size: 0.9em;
        color: #6c757d;
        margin-top: 30px;
        text-align: center;
    }
    .section-divider {
        margin: 40px 0;
        border-top: 2px solid #0056b3;
    }
</style>
</head>
<body>
    <h2>Daily Indian Stock Technical Analysis Report</h2>
    <p>Dear Kshitij,</p>
    <p>Here are the latest technical indicators for your selected Indian securities:</p>
'''

    # Add summary section at the top
    email_body_html += generate_summary_html(stocks_stats, etfs_stats, icici_stats)

    # Add stocks table
    email_body_html += generate_stock_table_html(stocks_suggestions, "Stocks Portfolio")

    # Add section divider
    email_body_html += '''
    <div class="section-divider"></div>
'''

    # Add ETFs table
    email_body_html += generate_etf_table_html(etfs_suggestions, "ETFs Portfolio (with TSI Analysis)")

    # Add section divider
    email_body_html += '''
    <div class="section-divider"></div>
'''

    # Add ICICI Direct Shubh Nivesh table
    email_body_html += generate_stock_table_html(icici_suggestions, "ICICI Direct Shubh Nivesh (Strong Business Fundamentals)")

    email_body_html += f'''
    <p><i>Note: RSI, MFI, EMA are momentum indicators. TSI (True Strength Index) uses double EMA smoothing for ETFs.</i></p>
    <p><i>🚀 "Strong Buy (TSI Crossover)" indicates TSI crossed above its signal line.</i></p>
    <p><i>⚠️ "Sell (TSI Crossover)" indicates TSI crossed below its signal line.</i></p>
    <p><i>📈 "EMA Diff Trend: Shortening" indicates EMA9 is approaching EMA26 (potential trend change)</i></p>
    <p><i>📉 "EMA Diff Trend: Widening" indicates EMA9 is moving away from EMA26 (trend strengthening)</i></p>
    <p><i>📊 "Min/Max RSI (4d)" shows the lowest and highest RSI values from the last 4 trading days</i></p>
    <p><i>💰 Investment Guidelines: Stocks - {STOCK_INVESTMENT_AMOUNT} per buy signal | ETFs - {ETF_INVESTMENT_AMOUNT} per buy signal</i></p>
    <p class="footer-text">Best regards,<br>Your Stock Analyst</p>
</body>
</html>
'''

    # Create the email message
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f'Daily Security Report (Kshitij): {stocks_stats["buy_count"] + etfs_stats["buy_count"] + icici_stats["buy_count"]} Buys, {stocks_stats["sell_count"] + etfs_stats["sell_count"] + icici_stats["sell_count"]} Sells'
    msg.add_alternative(email_body_html, subtype='html')

    # Send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully with HTML content!")
    except Exception as e:
        print(f"Error sending email: {e}")