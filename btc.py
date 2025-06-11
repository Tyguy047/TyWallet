'''
Bitcoin mainnet functionality is now enabled.
Please use with caution and ensure you have proper backups of your wallet data.
'''

import os
from bitcoinlib.wallets import Wallet
from bitcoinlib.mnemonic import Mnemonic
import requests
import json

def priceGrab():
    """Fetch current Bitcoin price from TyWallet API"""
    try:
        url = 'https://api.tywallet.xyz/prices/bitcoin'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Price fetch error: {e}")
        return "Error: Price data could not be fetched!"
    except Exception as e:
        print(f"Unexpected error in priceGrab: {e}")
        return "Error: Price data could not be fetched!"

def balanceCheck():
    """Check Bitcoin balance for the configured address"""
    def addressGrab():
        try:
            with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["addresses"].get("Bitcoin")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error reading Bitcoin address from config: {e}")
            return None

    ADDRESS = addressGrab()
    if not ADDRESS:
        return "Error: No Bitcoin address configured!"

    try:
        url = f"https://blockstream.info/api/address/{ADDRESS}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
        
        return {
            "confirmed_balance": f"{confirmed / 1e8:,.8f}",
            "unconfirmed_balance": f"{unconfirmed / 1e8:,.8f}"
        }
    except requests.RequestException as e:
        print(f"Balance check error: {e}")
        return "Network error: Could not fetch balance data!"
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
        return "Error: Invalid response from balance service!"
    except Exception as e:
        print(f"Unexpected error in balanceCheck: {e}")
        return "An error occurred when fetching your balance! Your funds are safe, this is likely a temporary service issue."

def walletGen():
    """Generate a new Bitcoin mainnet wallet"""
    try:
        # Generate a mnemonic seed phrase first
        mnemonic = Mnemonic()
        seed_phrase = mnemonic.generate(strength=256)  # 256 bits = 24 words
        
        # Create wallet with unique name and the generated mnemonic
        wallet_name = "Bitcoin"
        
        # Check if wallet already exists and delete it
        try:
            existing_wallet = Wallet(wallet_name)
            existing_wallet.delete()
            print(f"Deleted existing wallet: {wallet_name}")
        except:
            pass  # Wallet doesn't exist, which is fine
        
        # Create new wallet
        wallet = Wallet.create(wallet_name, keys=seed_phrase, network='bitcoin')
        print("Bitcoin mainnet wallet created successfully!")

        wallet_data = {
            "Name": str(wallet.name),
            "Network": str(wallet.network.name),
            "Address": str(wallet.get_key().address),
            "Public_Key": str(wallet.get_key().public()),
            "Private_Key_WIF": str(wallet.get_key().wif),
            "Seed": str(seed_phrase),
            "Created": "N/A"  # Remove the created attribute since it doesn't exist
        }
        
        # Ensure wallets directory exists
        wallets_dir = os.path.expanduser('~/TyWallet/Wallets')
        os.makedirs(wallets_dir, exist_ok=True)
        
        # Save wallet to file
        wallet_file = os.path.join(wallets_dir, f"{wallet.name}_bitcoin_mainnet.json")
        with open(wallet_file, 'w', encoding='utf-8') as f:
            json.dump(wallet_data, f, indent=2)
        
        print(f"Wallet saved to: {wallet_file}")
        return wallet_data
        
    except Exception as e:
        print(f"Error generating wallet: {e}")
        return {"error": f"Failed to generate wallet: {str(e)}"}

def getWalletInstance():
    """Get the Bitcoin wallet instance"""
    try:
        wallet = Wallet('Bitcoin')
        return wallet
    except Exception as e:
        print(f"Error getting wallet instance: {e}")
        return None

def broadcastTx(tx_hex):
    """Broadcast a Bitcoin transaction to the network"""
    if not tx_hex:
        return "Error: No transaction data provided"
        
    url = "https://blockstream.info/api/tx"
    headers = {'Content-Type': 'text/plain'}
    
    try:
        response = requests.post(url, data=tx_hex, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text  # Returns the transaction ID
    except requests.RequestException as e:
        print(f"Broadcast error: {e}")
        return f"Broadcast failed: Network error - {str(e)}"
    except Exception as e:
        print(f"Unexpected broadcast error: {e}")
        return f"Broadcast failed: {str(e)}"

def smartFeeCalc():
    """Calculate smart fee based on network conditions"""
    try:
        # Try mempool.space first (most reliable)
        url = "https://mempool.space/api/v1/fees/recommended"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return max(data.get('fastestFee', 20), 10)  # Minimum 10 sat/vB
    except:
        try:
            # Fallback to blockstream
            url = "https://blockstream.info/api/fee-estimates"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Get 6 block target fee (about 1 hour)
            return max(int(data.get('6', 20)), 10)
        except:
            # Conservative fallback
            return 25  # 25 sat/vB

def validateAddress(address):
    """Validate Bitcoin address format"""
    if not address:
        return False
    
    # Basic Bitcoin address validation
    if len(address) < 26 or len(address) > 62:
        return False
    
    # Check for valid Bitcoin address prefixes
    valid_prefixes = ['1', '3', 'bc1']
    if not any(address.startswith(prefix) for prefix in valid_prefixes):
        return False
    
    return True

def sendBitcoin(RECEIVER_ADDRESS, AMOUNT):
    """Send Bitcoin to another address"""
    try:
        # Validate inputs
        if not validateAddress(RECEIVER_ADDRESS):
            return "Error: Invalid receiver address format"
        
        if AMOUNT <= 0:
            return "Error: Amount must be greater than 0"
        
        if AMOUNT > 21000000:  # More than total Bitcoin supply
            return "Error: Amount exceeds maximum possible Bitcoin supply"
        
        # Get dynamic fee
        FEE_PER_BYTE = smartFeeCalc()
        print(f"Using fee rate: {FEE_PER_BYTE} sat/vB")
        
        # Get wallet instance
        wallet = getWalletInstance()
        if not wallet:
            return "Error: Could not access Bitcoin wallet"
        
        # Rescan for UTXOs
        print("Scanning for available UTXOs...")
        wallet.scan()
        
        # Check wallet balance
        wallet_balance = wallet.balance()
        amount_satoshi = int(AMOUNT * 1e8)
        
        if wallet_balance < amount_satoshi:
            return f"Error: Insufficient balance. Available: {wallet_balance/1e8:.8f} BTC, Required: {AMOUNT:.8f} BTC"
        
        # Estimate transaction size and fee
        estimated_tx_size = 250  # Approximate size in bytes for 1 input, 2 outputs
        fee_total = FEE_PER_BYTE * estimated_tx_size
        
        # Check if we have enough for amount + fee
        if wallet_balance < (amount_satoshi + fee_total):
            max_sendable = (wallet_balance - fee_total) / 1e8
            return f"Error: Insufficient balance for amount + fees. Maximum sendable: {max_sendable:.8f} BTC"
        
        print(f"Creating transaction: {AMOUNT} BTC to {RECEIVER_ADDRESS}")
        print(f"Estimated fee: {fee_total/1e8:.8f} BTC ({FEE_PER_BYTE} sat/vB)")
        
        # Create and send transaction
        tx = wallet.send_to(
            RECEIVER_ADDRESS,
            amount_satoshi,
            fee=fee_total,
            min_confirms=0  # Allow unconfirmed UTXOs
        )
        
        if not tx:
            return "Error: Failed to create transaction"
        
        tx_hex = tx.as_hex()
        if not tx_hex:
            return "Error: Failed to serialize transaction"
        
        print(f"Transaction created successfully. Broadcasting...")
        result = broadcastTx(tx_hex)
        
        if result.startswith("Error") or result.startswith("Broadcast failed"):
            return result
        
        return f"Transaction sent successfully! TXID: {result}"
        
    except Exception as e:
        print(f"Error in sendBitcoin: {e}")
        return f"Error: Failed to send Bitcoin - {str(e)}"

def getTransactionHistory(limit=10):
    """Get transaction history for the Bitcoin address"""
    def addressGrab():
        try:
            with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["addresses"].get("Bitcoin")
        except:
            return None

    ADDRESS = addressGrab()
    if not ADDRESS:
        return []

    try:
        url = f"https://blockstream.info/api/address/{ADDRESS}/txs"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        transactions = response.json()
        
        # Format transactions for display
        formatted_txs = []
        for tx in transactions[:limit]:
            formatted_txs.append({
                'txid': tx['txid'],
                'confirmed': tx.get('status', {}).get('confirmed', False),
                'block_height': tx.get('status', {}).get('block_height', 0),
                'fee': tx.get('fee', 0) / 1e8 if tx.get('fee') else 0,
                'size': tx.get('size', 0)
            })
        
        return formatted_txs
    except Exception as e:
        print(f"Error fetching transaction history: {e}")
        return []