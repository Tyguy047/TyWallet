import requests
from utils import getCMC

def priceGrab():
    CMC_API = getCMC()
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': 'XMR',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_API,
        }

        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        xmr_price = data['data']['XMR']['quote']['USD']['price']
        return f"Bitcoin price is ${xmr_price:,.2f}"
    
    except Exception:
        return "Error: Price data could not be fetched!"