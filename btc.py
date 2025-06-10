import os
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
import requests
import json
from utils import getCMC

def priceGrab():
    try:
        url = 'https://api.tywallet.xyz/prices/bitcoin'
        response = requests.get(url)
        response.raise_for_status()
        return response.text
            
    except Exception:
        return "Error: Price data could not be fetched!"

def balanceCheck():

    def addressGrab():
        with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Bitcoin")

    ADDRESS = addressGrab()

    try:
        url = f"https://blockstream.info/testnet/api/address/{ADDRESS}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
        
        return {
            "confirmed_balance": f"{confirmed / 1e8:,.8f}",
            "unconfirmed_balance": f"{unconfirmed / 1e8:,.8f}"
        }

    except Exception:
        return "An error occured when fetching your balance! Don't worry your funds are most likley okay this is probably an error on our end retreiving your balance!"

def walletGen():
    # Generate a mnemonic seed phrase first
    mnemonic = Mnemonic()
    seed_phrase = mnemonic.generate(strength=256)  # 256 bits = 24 words
    
    # Create wallet with unique name using timestamp and the generated mnemonic
    wallet_name = f"Bitcoin"
    wallet = Wallet.create(wallet_name, keys=seed_phrase, network='testnet')
    print("Wallet created!")

    wallet_data = {
        "Name": str(wallet.name),
        "Network": str(wallet.network.name),
        "Address": str(wallet.get_key().address),
        "Public key": str(wallet.get_key().public()) if hasattr(wallet.get_key(), 'public') else str(wallet.get_key()),
        "Private key (WIF)": str(wallet.get_key().wif),
        "Seed": str(seed_phrase),
    }
    
    # Save wallet to file
    wallet_file = os.path.join(os.path.expanduser('~/TyWallet/Wallets'), f"{wallet.name}_bitcoin_testnet.json")
    with open(wallet_file, 'w', encoding='utf-8') as f:
        json.dump(wallet_data, f, indent=2)
    
    print(f"Wallet saved to: {wallet_file}")
    
    return wallet_data

def broadcastTx(tx_hex):
    url = "https://blockstream.info/testnet/api/tx"
    headers = {'Content-Type': 'text/plain'}
    try:
        response = requests.post(url, data=tx_hex, headers=headers)
        response.raise_for_status()
        return response.text  # Returns the transaction ID
    except Exception as e:
        return f"Broadcast failed: {e}"

def sendBitcoin(RECEIVER_ADDRESS, AMOUNT):
    def smartFeeCalc():
        try:
            url = "https://mempool.space/api/v1/fees/recommended"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['fastestFee']
        except Exception:
            return 1
    FEE = smartFeeCalc()

    def rawTx(RECEIVER_ADDRESS, AMOUNT, FEE_PER_BYTE):
        wallet = Wallet('Bitcoin')
        wallet.scan()  # Rescan to make sure UTXOs are available

        amount_satoshi = int(AMOUNT * 1e8)
        estimated_tx_size = 250  # Approximate size in bytes
        fee_total = FEE_PER_BYTE * estimated_tx_size

        tx = wallet.send_to(
            RECEIVER_ADDRESS,
            amount_satoshi,
            fee=fee_total,
            min_confirms=0  # Allow unconfirmed UTXOs
        )

        return tx.as_hex()

    tx_hex = rawTx(RECEIVER_ADDRESS, AMOUNT, FEE)
    result = broadcastTx(tx_hex)
    return result