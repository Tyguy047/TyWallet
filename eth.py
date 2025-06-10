import requests
import web3
from eth_account import Account
import os
import json

def priceGrab():
    try:
        url = 'https://api.tywallet.xyz/prices/ethereum'
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception:
        return "Error: Price data could not be fetched!"

def walletGen():
    wallet_dir = os.path.expanduser("~/TyWallet")
    os.makedirs(wallet_dir, exist_ok=True)
    
    wallet_file = os.path.join(wallet_dir, "Ethereum_Wallet.json")
    if not os.path.exists(wallet_file):
        with open(wallet_file, 'w') as f:
            json.dump({}, f, indent=4)

    Account.enable_unaudited_hdwallet_features()

    # Generate a new account from a mnemonic seed
    account, mnemonic = Account.create_with_mnemonic()

    with open(wallet_file, 'r+') as f:
        wallet_data = json.load(f)
        wallet_data[account.address] = {
            "Private_Key": account.key.hex(),
            "Public_Key": account.address
        }
        f.seek(0)
        json.dump(wallet_data, f, indent=4)
        f.truncate()

    return {
        "Private_Key": account.key.hex(),
        "Public_Key": account.address,
        "Seed": mnemonic
    }

def balanceCheck():
    def addressGrab():
        with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Ethereum")

    ADDRESS = addressGrab()

    try:
        url = f"https://api.blockchair.com/ethereum/dashboards/address/{ADDRESS}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        balance = data['data'][ADDRESS]['address']['balance']
        return f"{balance / 1e18:,.8f}"

    except Exception:
        return "An error occured when fetching your balance! Don't worry your funds are most likley okay this is probably an error on our end retreiving your balance!"

def createTx(receiver, amount):

    def smartGas():
        try:
            url = 'https://api.blockchair.com/ethereum/stats'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # Convert gwei to wei (multiply by 1e9)
            gas_price_gwei = data['data']['avg_gas_price']
            return int(gas_price_gwei * 1e9)
        except Exception:
            return 20000000000  # 20 gwei in wei as fallback

    def addressGrab():
        try:
            with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["addresses"].get("Ethereum")
        except Exception:
            return None

    def getPrivateKey():
        try:
            address = addressGrab()
            if not address:
                return None
            wallet_file = os.path.expanduser("~/TyWallet/Ethereum_Wallet.json")
            with open(wallet_file, 'r') as f:
                wallet_data = json.load(f)
                return wallet_data[address]["Private_Key"]
        except Exception:
            return None

    try:
        # Validate inputs
        if not receiver or not amount:
            return "Error: Missing receiver address or amount"
            
        to_address = receiver
        tx_amount = float(amount)  # Amount in ETH
        fee = smartGas()  # Fetch average gas price
        
        from_address = addressGrab()
        private_key = getPrivateKey()
        
        if not from_address or not private_key:
            return "Error: Unable to retrieve wallet information"
        
        # Create offline transaction (without network connection)
        # Using default values for offline transaction creation
        tx = {
            'to': to_address,
            'value': int(tx_amount * 1e18),  # Convert ETH to Wei manually
            'gas': 21000,  # Standard gas limit for ETH transfer
            'gasPrice': fee,  # Gas price in wei from smartGas()
            'nonce': 0,  # Default nonce for offline mode
        }
        
        # Sign transaction offline
        w3 = web3.Web3()  # Create Web3 instance without provider for offline signing
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        return signed_tx.rawTransaction.hex()
        
    except Exception as e:
        return f"Error creating transaction: {str(e)}"

def broadcastTx(TX):
    url = 'https://cloudflare-eth.com'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": [TX],
        "id": 1
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get('result', 'Transaction hash not found')

    except Exception as e:
        return f"Error broadcasting transaction: {str(e)}"