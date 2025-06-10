import requests

def priceGrab():
    try:
        url = 'https://api.tywallet.xyz/prices/monero'
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception:
        return "Error: Price data could not be fetched!"