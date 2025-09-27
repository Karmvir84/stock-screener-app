import requests
from config import API_KEY

print("ਸਟਾਕ ਸਕਰੀਨਰ ਚੱਲ ਰਿਹਾ ਹੈ...")
print("ਇੰਤਜ਼ਾਰ ਕਰੋ, ਡੇਟਾ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...")

# Alpha Vantage API ਨਾਲ ਡੇਟਾ ਲੈਣ ਲਈ
url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}"

try:
    response = requests.get(url)
    data = response.json()
    
    print("\n" + "="*50)
    print("ਆਜ ਦੇ ਟਾਪ ਗੇਨਰਸ ਸਟਾਕਸ:")
    print("="*50)
    
    if 'top_gainers' in data:
        for i, stock in enumerate(data['top_gainers'][:10], 1):
            print(f"{i}. {stock['ticker']}: ${stock['price']} ({stock['change_percentage']})")
    else:
        print("ਕੋਈ ਡੇਟਾ ਨਹੀਂ ਮਿਲਿਆ")
        
except Exception as e:
    print(f"ਗਲਤੀ: {e}")
    print("API ਕੁੰਜੀ ਜਾਂ ਨੈੱਟਵਰਕ ਕਨੈਕਸ਼ਨ ਚੈੱਕ ਕਰੋ")

print("\n" + "="*50)
input("ਬੰਦ ਕਰਨ ਲਈ Enter ਦਬਾਓ...")
