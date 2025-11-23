# config.py

# Stock and ETF Lists
STOCKS = ['VMM.NS','MEDANTA.NS','PERSISTENT.NS','COFORGE.NS','BALKRISIND.NS','MFSL.NS','HDFCBANK.NS','ICICIBANK.NS','BLUESTARCO.NS']
ETFS = ['MAHKTECH.NS','MAFANG.NS','PHARMABEES.NS','NIFTYBEES.NS','GOLDBEES.NS','ICICIB22.NS','ITBEES.NS','HDFCSML250.NS','PSUBANK.NS','AUTOBEES.NS','GROWWRAIL.NS','MODEFENCE.NS']

# ICICI Direct Shubh Nivesh Stocks
ICICI_SHUBH_NIVESH_STOCKS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
                            'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS']

# Security Name Mappings
SECURITY_NAMES = {
    'BLUESTARCO.NS':'Blue Star Co.',
    'VMM.NS':'Vishal Mega Mart',
    'MEDANTA.NS': 'Medanta',
    'PERSISTENT.NS':'Persistant System',
    'COFORGE.NS':'Coforge',
    'BALKRISIND.NS':'Balkrishna Industries',
    'MFSL.NS':'Max Financial Service',
    'HDFCBANK.NS':'HDFC Bank',
    'ICICIBANK.NS':'ICICI Bank',
    'NIFTYBEES.NS': 'Nifty 50',
    'GOLDBEES.NS': 'Gold ETF',
    'SILVERBEES.NS':'Silver ETF',
    'ITBEES.NS': 'Nifty IT ETF',
    'HDFCSML250.NS': 'SmallCap 150 Index Fund',
    'PSUBANK.NS':'PSU Bank ETF',
    'AUTOBEES.NS':'AUTO ETF',
    'GROWWRAIL.NS':'Railway ETF',
    'MODEFENCE.NS':'Defence ETF',
    'PHARMABEES.NS':'Nippon Farma ETF',
    'MAFANG.NS':'NYSE Fang ETF',
    'MAHKTECH.NS':'Hang Seng Tech ETF'
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

# Email Configuration
SENDER_EMAIL = 'patel1.kshitij@gmail.com'
SENDER_PASSWORD = ''
RECIPIENT_EMAIL = ['kshitijpatel917050@gmail.com','mohitamalner@gmail.com']

# Investment Guidelines
STOCK_INVESTMENT_AMOUNT = "₹25,000"
ETF_INVESTMENT_AMOUNT = "₹50,000"

# Database Configuration
DB_FILE = 'stock_purchases.db'