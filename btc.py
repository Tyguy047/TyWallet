from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes
from bitcoinlib.transactions import Transaction
from bitcoinlib.wallets import Wallet
from bitcoinlib.keys import HDKey
import requests
import json
import os
from utils import getCMC

def priceGrab():
    CMC_API = getCMC()
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': 'BTC',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_API,  # Replace with your actual API key
        }

        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        btc_price = data['data']['BTC']['quote']['USD']['price']
        return f"Bitcoin price is ${btc_price:,.2f}"
            
    except Exception:
        return "Error: Price data could not be fetched!"

def balanceCheck():

    def addressGrab():
        with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Bitcoin")

    ADDRESS = addressGrab()

    try:
        url = f"https://blockstream.info/api/address/{ADDRESS}"
        response = requests.get(url)
        data = response.json()
        
        confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
        
        return {
            "confirmed_balance": confirmed / 1e8,
            "unconfirmed_balance": unconfirmed / 1e8
        }

    except Exception:
        return "An error occured when fetching your balance! Don't worry your funds are most likley okay this is probably an error on our end retreiving your balance!"

def walletGen():
    def generate_seed():
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(24)
        # print("Mnemonic (Seed Phrase):", str(mnemonic))
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        return str(mnemonic), seed_bytes

    def generate_wallet(seed_bytes):
        bip84_wallet = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
        account = bip84_wallet.Purpose().Coin().Account(0)
        change = account.Change(Bip44Changes.CHAIN_EXT)
        return change

    def get_private_key(change):
        priv_key = change.AddressIndex(0).PrivateKey().ToWif()
        # print("Private Key (WIF):", priv_key)
        return priv_key

    def get_public_info(change):
        pub_key = change.AddressIndex(0).PublicKey()
        pub_key_hex = pub_key.RawCompressed().ToHex()
        address = pub_key.ToAddress()
        # print("Public Key (Compressed):", pub_key_hex)
        # print("Bitcoin Address:", address)
        return pub_key_hex, address

    # --- Run generation
    mnemonic, seed_bytes = generate_seed()
    change = generate_wallet(seed_bytes)
    pub_key_hex, address = get_public_info(change)
    priv_key = get_private_key(change)

    return {
        "mnemonic": mnemonic,
        "private_key": priv_key,
        "public_key": pub_key_hex,
        "address": address
    }

def sendBTC(receiver_address, amount, private_key):
    def makeRawTx():
        # Derive address from private key WIF
        key = HDKey(import_key=private_key)
        address = key.address()

        # Fetch UTXOs
        url = f"https://blockstream.info/api/address/{address}/utxo"
        response = requests.get(url)
        utxos = response.json()

        inputs = []
        total_available = 0
        for utxo in utxos:
            inputs.append({
                'txid': utxo['txid'],
                'vout': utxo['vout'],
                'value': utxo['value']
            })
            total_available += utxo['value']

        send_value = int(float(amount) * 1e8)

        # Estimate transaction size
        num_inputs = len(inputs)
        num_outputs = 2  # receiver + change
        tx_size = 10 + num_inputs * 148 + num_outputs * 34

        # Fetch fee rate (satoshis per byte) from mempool.space
        try:
            fee_api_url = 'https://mempool.space/api/v1/fees/recommended'
            fee_response = requests.get(fee_api_url)
            fee_data = fee_response.json()
            fee_rate = fee_data.get('fastestFee', 10)  # fallback to 10 if API fails
        except Exception:
            fee_rate = 10

        fee = tx_size * fee_rate

        change = total_available - send_value - fee
        if change < 0:
            raise ValueError("Insufficient funds for amount + fee")

        # Build outputs
        outputs = [
            (receiver_address, send_value),
        ]
        if change > 0:
            outputs.append((address, change))

        # Create transaction
        tx = Transaction(network='bitcoin')
        for inp in inputs:
            tx.add_input(prev_hash=inp['txid'], output_n=inp['vout'], value=inp['value'], address=address)

        for out_addr, out_value in outputs:
            tx.add_output(address=out_addr, value=out_value)

        # Sign transaction inputs
        for i in range(len(inputs)):
            tx.sign(i, key.wif())

        # Return raw transaction hex
        return tx.as_hex()
    
    TX = makeRawTx()

    def broadcastTx(raw_tx_hex):
        url = "https://blockstream.info/api/tx"
        headers = {'Content-Type': 'text/plain'}
        response = requests.post(url, data=raw_tx_hex, headers=headers)
        if response.status_code == 200:
            return response.text  # Returns the txid if successful
        else:
            raise Exception(f"Broadcast failed: {response.status_code} - {response.text}")

    txid = broadcastTx(TX)
    print("Transaction broadcasted with txid:", txid)