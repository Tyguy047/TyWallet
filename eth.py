import web3
import requests

def priceGrab():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd"
        }

        response = requests.get(url, params=params)
        data = response.json()
        price = data["ethereum"]["usd"]
        return f"${price:,.2f}"
    
    except Exception:
        return "Error: Price data could not be fetched!"