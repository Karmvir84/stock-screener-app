from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
import time
import threading
from datetime import datetime

app = Flask(_name_)

# Global variable to store results
intraday_results = []
last_updated = ""

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

def run_intraday_screener():
    global intraday_results, last_updated
    
    while True:
        try:
            stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
            
            good_stocks = []
            for symbol in stocks:
                print(f"Scanning {symbol}...")
                data = get_intraday_data(symbol)
                if check_intraday_signals(data):
                    good_stocks.append(symbol)
            
            intraday_results = good_stocks
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Scan completed at {last_updated}: {good_stocks}")
            
        except Exception as e:
            print(f"Screener error: {e}")
        
        # Wait for 5 minutes (300 seconds) before next scan
        time.sleep(300)

@app.route('/')
def index():
    stocks_text = "\n".join([f"📈 {stock}" for stock in intraday_results]) if intraday_results else "❌ No stocks found"
    return f"""
    <html>
        <head>
            <title>Stock Screener</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f0f0f0; }}
                .container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .stock {{ color: green; font-weight: bold; margin: 5px 0; }}
                .timestamp {{ color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Intraday Stock Screener</h1>
                <div class="timestamp">Last Updated: {last_updated}</div>
                <pre>{stocks_text}</pre>
                <p>Auto-refreshes every 30 seconds</p>
            </div>
        </body>
    </html>
    """

@app.route('/intraday')
def intraday_api():
    return jsonify({
        'stocks': intraday_results,
        'last_updated': last_updated,
        'count': len(intraday_results)
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': last_updated})

if _name_ == '_main_':
    # Start the screener in a separate thread
    screener_thread = threading.Thread(target=run_intraday_screener)
    screener_thread.daemon = True
    screener_thread.start()
    
    print("Stock Screener started!")
    print("Web interface available at: http://localhost:5000")
    print("API available at: http://localhost:5000/intraday")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
