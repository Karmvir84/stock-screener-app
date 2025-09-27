from flask import Flask
import yfinance as yf
import pandas as pd
import schedule
import time
import threading

app = Flask(__name__)

def get_intraday_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def check_intraday_signals(data):
    if data is None or len(data) < 2:
        return False
    
    current = data.iloc[-1]
    previous = data.iloc[-2]
    
    volume_breakout = current['Volume'] > previous['Volume'] * 1.5
    price_surge = ((current['Close'] - previous['Close']) / previous['Close']) * 100 > 2.0
    
    return volume_breakout and price_surge

intraday_results = []

def run_intraday_screener():
    global intraday_results
    stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
    
    good_stocks = []
    for symbol in stocks:
        data = get_intraday_data(symbol)
        if check_intraday_signals(data):
            good_stocks.append(symbol)
    
    intraday_results = good_stocks
    print(f"Scanned: {good_stocks}")

def start_scheduler():
    schedule.every(5).minutes.do(run_intraday_screener)
    run_intraday_screener()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    stocks_text = "\n".join([f"📈 {stock}" for stock in intraday_results]) if intraday_results else "❌ No stocks found"
    return f"<html><body><h1>Stock Screener</h1><pre>{stocks_text}</pre></body></html>"

@app.route('/intraday')
def intraday():
    return {'stocks': intraday_results}

if _name_ == '_main_':
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    app.run(debug=True)
