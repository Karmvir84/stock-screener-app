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
        print(f"Error: {e}")
        return None

def check_signals(data):
    if data is None or len(data) < 2:
        return False
    current = data.iloc[-1]
    previous = data.iloc[-2]
    volume_ok = current['Volume'] > previous['Volume'] * 1.5
    price_ok = ((current['Close'] - previous['Close']) / previous['Close']) * 100 > 2.0
    return volume_ok and price_ok

intraday_results = []

def run_screener():
    global intraday_results
    stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS']
    good_stocks = []
    
    for symbol in stocks:
        data = get_intraday_data(symbol)
        if check_signals(data):
            good_stocks.append(symbol)
    
    intraday_results = good_stocks
    print(f"Scanned: {good_stocks}")

def scheduler():
    schedule.every(2).minutes.do(run_screener)
    run_screener()
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def home():
    stocks_text = "\n".join(intraday_results) if intraday_results else "No stocks found"
    return f"<h1>Stock Screener</h1><pre>{stocks_text}</pre>"

if _name_ == '_main_':
    thread = threading.Thread(target=scheduler)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
