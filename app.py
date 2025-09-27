# app.py
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IntraDayStockScreener:
    def __init__(self):
        self.today = datetime.now().date()
        self.screened_stocks = []
    
    def get_stock_data(self, symbol, period='1d', interval='5m'):
        """Stock data fetch karta hai with error handling"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, data):
        """Technical indicators calculate karta hai"""
        if data is None or len(data) < 20:
            return None
        
        try:
            # Simple Moving Averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_5'] = data['Close'].rolling(window=5).mean()
            
            # RSI Calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Volume SMA
            data['Volume_SMA'] = data['Volume'].rolling(window=10).mean()
            
            return data
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return None
    
    def apply_screening_rules(self, data, symbol):
        """Intraday screening rules apply karta hai"""
        if data is None or len(data) < 20:
            return False
        
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            # Screening Criteria
            condition1 = latest['Close'] > latest['SMA_20']  # Price above 20 SMA
            condition2 = latest['SMA_5'] > latest['SMA_20']  # 5 SMA above 20 SMA
            condition3 = latest['RSI'] > 30 and latest['RSI'] < 70  # RSI in range
            condition4 = latest['Volume'] > latest['Volume_SMA'] * 1.5  # Volume spike
            condition5 = latest['Close'] > latest['Open']  # Green candle
            
            if condition1 and condition2 and condition3 and condition4 and condition5:
                return {
                    'Symbol': symbol,
                    'Price': round(latest['Close'], 2),
                    'Change %': round(((latest['Close'] - prev['Close']) / prev['Close']) * 100, 2),
                    'Volume': latest['Volume'],
                    'RSI': round(latest['RSI'], 2),
                    'SMA_20': round(latest['SMA_20'], 2)
                }
            return False
        except Exception as e:
            print(f"Error applying screening rules for {symbol}: {e}")
            return False
    
    def screen_stocks(self, stock_list):
        """Main screening function"""
        print("Intraday Stock Screening Shuru ho raha hai...")
        print("=" * 60)
        
        screened_stocks = []
        
        for symbol in stock_list:
            try:
                data = self.get_stock_data(symbol)
                data_with_indicators = self.calculate_indicators(data)
                result = self.apply_screening_rules(data_with_indicators, symbol)
                
                if result:
                    screened_stocks.append(result)
                    print(f"✓ {symbol} - Passed screening")
                else:
                    print(f"✗ {symbol} - Did not pass criteria")
                    
            except Exception as e:
                print(f"✗ {symbol} - Error: {e}")
                continue
        
        return screened_stocks
    
    def display_results(self, screened_stocks):
        """Results display karta hai"""
        print("\n" + "=" * 60)
        print("SCREENING RESULTS")
        print("=" * 60)
        
        if not screened_stocks:
            print("Koi stocks screening criteria pass nahi kiye!")
            return
        
        df = pd.DataFrame(screened_stocks)
        df = df.sort_values('Change %', ascending=False)
        print(df.to_string(index=False))

def main():
    """Main function"""
    try:
        # Sample stock list (aap apne stocks add kar sakte hain)
        stock_list = [
            'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS',
            'AXISBANK.NS', 'LT.NS', 'MARUTI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS'
        ]
        
        # Screener object create karna
        screener = IntraDayStockScreener()
        
        # Screening process start karna
        screened_stocks = screener.screen_stocks(stock_list)
        
        # Results display karna
        screener.display_results(screened_stocks)
        
    except Exception as e:
        print(f"Main function mein error: {e}")

if __name__ == "__main__":
    main()
