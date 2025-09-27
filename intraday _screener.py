# intraday_screener.py
import yfinance as yf
import pandas as pd
import time
import schedule

def get_stock_data(symbol):
    """ਸਟਾਕ ਦਾ ਡੇਟਾ ਲੈਂਦਾ ਹੈ"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def check_volume_breakout(current_volume, avg_volume):
    """ਵਾਲੀਊਮ ਵਧਣ ਦੀ ਜਾਂਚ ਕਰਦਾ ਹੈ"""
    if current_volume > avg_volume * 1.5:
        return True
    return False

def check_price_surge(current_price, previous_close):
    """ਕੀਮਤ ਵਧਣ ਦੀ ਜਾਂਚ ਕਰਦਾ ਹੈ"""
    if previous_close == 0:
        return False
    price_change = ((current_price - previous_close) / previous_close) * 100
    if price_change > 2.0:
        return True
    return False

def screen_intraday_stocks():
    """ਮੁੱਖ ਸਕਰੀਨਿੰਗ ਫੰਕਸ਼ਨ"""
    print("🔍 ਇੰਟਰਾਡੇ ਸਕਰੀਨਰ ਚੱਲ ਰਿਹਾ ਹੈ...")
    
    # ਭਾਰਤੀ ਸਟਾਕਾਂ ਦੀ ਲਿਸਟ
    stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
    
    good_stocks = []
    
    for symbol in stocks:
        data = get_stock_data(symbol)
        
        if data is not None and len(data) >= 2:
            current_candle = data.iloc[-1]
            previous_candle = data.iloc[-2]
            
            # ਨਿਯਮ ਚੈੱਕ ਕਰੋ
            volume_ok = check_volume_breakout(
                current_candle['Volume'], 
                previous_candle['Volume']
            )
            
            price_ok = check_price_surge(
                current_candle['Close'], 
                previous_candle['Close']
            )
            
            if volume_ok and price_ok:
                good_stocks.append({
                    'symbol': symbol,
                    'price': round(current_candle['Close'], 2),
                    'volume': current_candle['Volume']
                })
    
    # ਨਤੀਜੇ ਦਿਖਾਓ
    if good_stocks:
        print("🎯 ਚੰਗੇ ਇੰਟਰਾਡੇ ਸਟਾਕਸ:")
        for stock in good_stocks:
            print(f"📈 {stock['symbol']} - ਕੀਮਤ: ₹{stock['price']}")
    else:
        print("❌ ਇਸ ਸਮੇਂ ਕੋਈ ਚੰਗਾ ਸਟਾਕ ਨਹੀਂ ਮਿਲਿਆ")
    
    print("-" * 50)

if _name_ == "_main_":
    # ਹਰ 5 ਮਿੰਟ ਬਾਅਦ ਚਲਾਓ
    schedule.every(5).minutes.do(screen_intraday_stocks)
    
    # ਪਹਿਲਾਂ ਇੱਕ ਵਾਰ ਚਲਾਓ
    screen_intraday_stocks()
    
    # ਲੱਗਾਤਾਰ ਚਲਾਉਂਦੇ ਰਹੋ
    while True:
        schedule.run_pending()
        time.sleep(1)
