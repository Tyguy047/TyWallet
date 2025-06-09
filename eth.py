import web3
import requests
from utils import getCMC

def priceGrab():
    CMC_API = getCMC()
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': 'ETH',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_API,  # Replace with your actual API key
        }

        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        eth_price = data['data']['ETH']['quote']['USD']['price']
        return f"Bitcoin price is ${eth_price:,.2f}"
    
    except Exception:
        return "Error: Price data could not be fetched!"