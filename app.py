from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import schedule
import time
import threading

app = Flask(_name_)

# ਇੰਟਰਾਡੇ ਸਕਰੀਨਿੰਗ ਫੰਕਸ਼ਨਸ
def get_intraday_data(symbol):
    """ਸਟਾਕ ਦਾ ਇੰਟਰਾਡੇ ਡੇਟਾ ਲੈਂਦਾ ਹੈ"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def check_intraday_signals(data):
    """ਇੰਟਰਾਡੇ ਸਿਗਨਲ ਚੈੱਕ ਕਰਦਾ ਹੈ"""
    if data is None or len(data) < 2:
        return False
    
    current = data.iloc[-1]
    previous = data.iloc[-2]
    
    # ਵਾਲੀਊਮ ਬ੍ਰੇਕਆਊਟ
    volume_breakout = current['Volume'] > previous['Volume'] * 1.5
    
    # ਕੀਮਤ ਵਾਧਾ
    price_surge = ((current['Close'] - previous['Close']) / previous['Close']) * 100 > 2.0
    
    return volume_breakout and price_surge

# ਗਲੋਬਲ ਵੇਰੀਏਬਲ ਨਤੀਜਿਆਂ ਲਈ
intraday_results = []

def run_intraday_screener():
    """ਇੰਟਰਾਡੇ ਸਕਰੀਨਰ ਚਲਾਉਂਦਾ ਹੈ"""
    global intraday_results
    stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
    
    good_stocks = []
    for symbol in stocks:
        data = get_intraday_data(symbol)
        if check_intraday_signals(data):
            good_stocks.append(symbol)
    
    intraday_results = good_stocks
    print(f"🔄 ਇੰਟਰਾਡੇ ਸਕੈਨ ਕੀਤਾ: {good_stocks}")

# ਬੈਕਗ੍ਰਾਊਂਡ ਵਿੱਚ ਸਕਰੀਨਰ ਚਲਾਉਣ ਲਈ
def start_scheduler():
    """ਹਰ 5 ਮਿੰਟ ਬਾਅਦ ਸਕਰੀਨਰ ਚਲਾਉਂਦਾ ਹੈ"""
    schedule.every(5).minutes.do(run_intraday_screener)
    run_intraday_screener()  # ਪਹਿਲਾਂ ਇੱਕ ਵਾਰ ਚਲਾਓ
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# ਰੂਟਸ
@app.route('/')
def index():
    """ਮੁੱਖ ਪੇਜ"""
    return render_template('index.html', intraday_stocks=intraday_results)

@app.route('/intraday')
def intraday():
    """ਸਿਰਫ ਇੰਟਰਾਡੇ ਨਤੀਜੇ ਦਿਖਾਉਂਦਾ ਹੈ"""
    return {
        'status': 'success',
        'intraday_stocks': intraday_results,
        'count': len(intraday_results)
    }

if _name_ == '_main_':
    # ਬੈਕਗ੍ਰਾਊਂਡ ਸਕਰੀਨਰ ਸ਼ੁਰੂ ਕਰੋ
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Flask ਐਪ ਚਲਾਓ
    app.run(debug=True)
