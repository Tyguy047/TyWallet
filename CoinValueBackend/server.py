from flask import Flask
from flask_cors import CORS
import requests
import time
import os
import threading
from dotenv import load_dotenv
load_dotenv()

CMC_API = os.getenv('CMC_API')

app = Flask(__name__)
CORS(app)

# Global cache for prices
price_cache = {
    'bitcoin': "Loading...",
    'monero': "Loading...", 
    'ethereum': "Loading..."
}

def fetch_price(symbol, coin_key):
    """Fetch price for a specific cryptocurrency"""
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': symbol,
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_API,
        }

        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()
        data = response.json()
        price = data['data'][symbol]['quote']['USD']['price']
        price_cache[coin_key] = f"{price:,.2f}"
    except Exception:
        price_cache[coin_key] = "Error: Price data could not be fetched!"

def update_all_prices():
    """Update all cryptocurrency prices"""
    fetch_price('BTC', 'bitcoin')
    fetch_price('XMR', 'monero')
    fetch_price('ETH', 'ethereum')

def price_updater():
    """Background thread function to update prices every 540 seconds"""
    while True:
        update_all_prices()
        time.sleep(540)

# Start the background price updater thread
price_thread = threading.Thread(target=price_updater, daemon=True)
price_thread.start()

# Initial price fetch
update_all_prices()

@app.route('/')
def main():
    return """
    <html>
    <head>
        <title>TyWallet API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
            ul { margin: 10px 0; }
            li { margin: 5px 0; }
            .endpoint { background-color: #f4f4f4; padding: 5px; border-radius: 3px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>Welcome to the TyWallet API!</h1>
        <h2>(Scroll Down For Endpoints)</h2>
        <p>Anyone can use this API for their projects but please consider making a donation so we can run more servers and keep this API stable and free!</p>
        
        <h2>Community & Support</h2>
        <ul>
            <li><strong>My Personal Website</strong> <a href="https://www.tylercaselli.com">https://www.tylercaselli.com</a></li>
            <li><strong>Project Website:</strong> <a href="https://tywallet.xyz">https://tywallet.xyz</a></li>
            <li><strong>Discord:</strong> Not Online Yet!</li>
            <li><strong>GitHub:</strong> <a href="https://github.com/Tyguy047/TyWallet">https://github.com/Tyguy047/TyWallet</a></li>
            <li><strong>Email:</strong> <a href="mailto:getintouch@tylercaselli.com">getintouch@tylercaselli.com</a></li>
        </ul>

        <h2>Donations</h2>
        <ul>
            <li><strong>Bitcoin:</strong> Not Online Yet!</li>
            <li><strong>Monero:</strong> Not Online Yet!</li>
            <li><strong>Ethereum:</strong> Not Online Yet!</li>
        </ul>
        
        <h2>Testnet Coins for Developers</h2>
        <p>If you would like to help the development of new crypto wallets, consider sending us some testnet coins we can give to devs!</p>
        <ul>
            <li><strong>Bitcoin Testnet:</strong> Not Online Yet!</li>
        </ul>
        
        <p>I try to work on this whenever I have a chance so please be patient if you find a bug or something is not working as expected, I will try to fix it as soon as I can!</p>
        
        <h2>API Endpoints (As of now all endpoints only return USD conversions of the selected coin)</h2>
        <ul>
            <li><span class="endpoint">https://api.tywallet.xyz/prices/bitcoin</span></li>
            <li><span class="endpoint">https://api.tywallet.xyz/prices/monero</span></li>
            <li><span class="endpoint">https://api.tywallet.xyz/prices/ethereum</span></li>
        </ul>
        
        <h2>Privacy-Focused .onion Endpoints</h2>
        <p>Hey you like privacy online? Cool me too! Here's some .onion link endpoints you can use if you are running a hidden service or just don't want my VPS provider or myself to have your IP:</p>
        <ul>
            <li><span class="endpoint">http://cbckdpjeksawellm4z2ttub3vmn552hnaagrsjueugfs4bzk5lzcyqqd.onion/prices/bitcoin</span></li>
            <li><span class="endpoint">http://cbckdpjeksawellm4z2ttub3vmn552hnaagrsjueugfs4bzk5lzcyqqd.onion/prices/monero</span></li>
            <li><span class="endpoint">http://cbckdpjeksawellm4z2ttub3vmn552hnaagrsjueugfs4bzk5lzcyqqd.onion/prices/ethereum</span></li>
        </ul>
        
        <p><strong>Thank you for using TyWallet API!</strong></p>
    </body>
    </html>
    """


@app.route('/prices/bitcoin')
def bitcoin_price():
    return price_cache['bitcoin']


@app.route('/prices/monero')
def monero_price():
    return price_cache['monero']


@app.route('/prices/ethereum')
def ethereum_price():
    return price_cache['ethereum']

if __name__ == '__main__':
    app.run(debug=True)