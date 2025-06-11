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

    # Sync wallet address with config first
    syncWalletAddress()
    
    ADDRESS = addressGrab()
    if not ADDRESS:
        return "Error: No Bitcoin address configured!"

    # First try to get balance from wallet instance (more reliable for spending)
    try:
        wallet = getWalletInstance()
        if wallet:
            wallet.scan()  # Rescan for UTXOs
            wallet_balance = wallet.balance()
            wallet_balance_btc = wallet_balance / 1e8
            
            # If wallet has balance, use it as primary source
            if wallet_balance > 0:
                return {
                    "confirmed_balance": f"{wallet_balance_btc:.8f}",
                    "unconfirmed_balance": "0.00000000",
                    "source": "wallet"
                }
    except Exception as e:
        print(f"Wallet balance check error: {e}")

    # Fallback to external API
    try:
        url = f"https://blockstream.info/api/address/{ADDRESS}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        confirmed = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        unconfirmed = data['mempool_stats']['funded_txo_sum'] - data['mempool_stats']['spent_txo_sum']
        
        return {
            "confirmed_balance": f"{confirmed / 1e8:,.8f}",
            "unconfirmed_balance": f"{unconfirmed / 1e8:,.8f}",
            "source": "api"
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

        wallet_address = str(wallet.get_key().address)
        
        wallet_data = {
            "Name": str(wallet.name),
            "Network": str(wallet.network.name),
            "Address": wallet_address,
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
        
        # Update config.json with the correct address
        config_path = os.path.expanduser('~/TyWallet/config.json')
        try:
            with open(config_path, 'r+', encoding='utf-8') as config:
                data = json.load(config)
                data["addresses"]["Bitcoin"] = wallet_address
                config.seek(0)
                json.dump(data, config, indent=4)
                config.truncate()
            print(f"Updated config with wallet address: {wallet_address}")
        except Exception as e:
            print(f"Warning: Could not update config file: {e}")
        
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
    """Broadcast a Bitcoin transaction to the network with multiple endpoint fallbacks"""
    if not tx_hex:
        return "Error: No transaction data provided"
    
    # Multiple broadcast endpoints for better reliability - mempool.space prioritized
    endpoints = [
        {
            'name': 'Mempool.space',
            'url': 'https://mempool.space/api/tx',
            'headers': {'Content-Type': 'text/plain'},
            'method': 'POST', 
            'data': tx_hex
        },
        {
            'name': 'Blockstream',
            'url': 'https://blockstream.info/api/tx',
            'headers': {'Content-Type': 'text/plain'},
            'method': 'POST',
            'data': tx_hex
        },
        {
            'name': 'BlockCypher',
            'url': 'https://api.blockcypher.com/v1/btc/main/txs/push',
            'headers': {'Content-Type': 'application/json'},
            'method': 'POST',
            'data': '{"tx": "' + tx_hex + '"}'
        }
    ]
    
    last_error = None
    
    for endpoint in endpoints:
        try:
            print(f"Trying to broadcast via {endpoint['name']}...")
            
            if endpoint['name'] == 'BlockCypher':
                response = requests.post(
                    endpoint['url'], 
                    data=endpoint['data'],
                    headers=endpoint['headers'], 
                    timeout=30
                )
            else:
                response = requests.post(
                    endpoint['url'], 
                    data=endpoint['data'],
                    headers=endpoint['headers'], 
                    timeout=30
                )
            
            response.raise_for_status()
            
            # Parse response based on endpoint
            if endpoint['name'] == 'BlockCypher':
                result = response.json()
                if result.get('hash'):
                    print(f"Successfully broadcast via {endpoint['name']}")
                    return result['hash']
                else:
                    last_error = f"{endpoint['name']}: {result.get('error', 'Unknown error')}"
            else:
                result = response.text.strip()
                if result and len(result) == 64:  # Bitcoin transaction ID length
                    print(f"Successfully broadcast via {endpoint['name']}")
                    return result
                else:
                    last_error = f"{endpoint['name']}: Invalid response - {result}"
            
        except requests.RequestException as e:
            last_error = f"{endpoint['name']} network error: {str(e)}"
            print(f"Broadcast failed via {endpoint['name']}: {e}")
            continue
        except Exception as e:
            last_error = f"{endpoint['name']} error: {str(e)}"
            print(f"Unexpected error with {endpoint['name']}: {e}")
            continue
    
    return f"Broadcast failed: All endpoints failed. Last error: {last_error}"

def smartFeeCalc(balance_satoshi=None):
    """Calculate smart fee based on network conditions and balance"""
    try:
        # Try mempool.space first (most reliable)
        url = "https://mempool.space/api/v1/fees/recommended"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # For very small balances, use the economy fee rate
        if balance_satoshi and balance_satoshi < 5000:  # Less than 0.00005 BTC
            economy_fee = data.get('economyFee', 1)
            return max(economy_fee, 1)  # Minimum 1 sat/vB for dust amounts
        
        return max(data.get('fastestFee', 20), 10)  # Minimum 10 sat/vB
    except:
        try:
            # Fallback to blockstream
            url = "https://blockstream.info/api/fee-estimates"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # For small balances, use a lower fee target
            if balance_satoshi and balance_satoshi < 5000:
                # Use 144 block target (about 24 hours) for small amounts
                return max(int(data.get('144', 1)), 1)
            
            # Get 6 block target fee (about 1 hour)
            return max(int(data.get('6', 20)), 10)
        except:
            # Conservative fallback - lower for small balances
            if balance_satoshi and balance_satoshi < 5000:
                return 2  # 2 sat/vB for small amounts
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
        
        # Sync wallet address with config first
        syncWalletAddress()
        
        # Get wallet instance
        wallet = getWalletInstance()
        if not wallet:
            return "Error: Could not access Bitcoin wallet"
        
        # Rescan for UTXOs
        print("Scanning for available UTXOs...")
        wallet.scan()
        
        # Check wallet balance first
        wallet_balance = wallet.balance()
        
        # Get dynamic fee based on balance
        FEE_PER_BYTE = smartFeeCalc(wallet_balance)
        print(f"Using fee rate: {FEE_PER_BYTE} sat/vB")
        
        amount_satoshi = int(AMOUNT * 1e8)
        
        # Estimate transaction size and fee first
        estimated_tx_size = 250  # Approximate size in bytes for 1 input, 2 outputs
        fee_total = FEE_PER_BYTE * estimated_tx_size
        
        # Check if balance is too small for any transaction
        if wallet_balance <= fee_total:
            return f"Error: Balance too small for any transaction. Available: {wallet_balance/1e8:.8f} BTC, Minimum fee required: {fee_total/1e8:.8f} BTC. Consider consolidating UTXOs or waiting for lower network fees."
        
        # Calculate maximum sendable amount
        max_sendable_satoshi = wallet_balance - fee_total
        max_sendable_btc = max_sendable_satoshi / 1e8
        
        if wallet_balance < amount_satoshi:
            return f"Error: Insufficient balance. Available: {wallet_balance/1e8:.8f} BTC, Required: {AMOUNT:.8f} BTC, Maximum sendable: {max_sendable_btc:.8f} BTC"
        
        # Check if we have enough for amount + fee
        if wallet_balance < (amount_satoshi + fee_total):
            return f"Error: Insufficient balance for amount + fees. Available: {wallet_balance/1e8:.8f} BTC, Required (amount + fee): {(amount_satoshi + fee_total)/1e8:.8f} BTC, Maximum sendable: {max_sendable_btc:.8f} BTC"
        
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

def sweepBitcoin(RECEIVER_ADDRESS):
    """Send all available Bitcoin (minus fees) to another address"""
    try:
        # Validate inputs
        if not validateAddress(RECEIVER_ADDRESS):
            return "Error: Invalid receiver address format"
        
        # Sync wallet address with config first
        syncWalletAddress()
        
        # Get wallet instance
        wallet = getWalletInstance()
        if not wallet:
            return "Error: Could not access Bitcoin wallet"
        
        # Rescan for UTXOs
        print("Scanning for available UTXOs...")
        wallet.scan()
        
        # Check wallet balance
        wallet_balance = wallet.balance()
        
        if wallet_balance <= 0:
            return "Error: No balance available to sweep"
        
        # Get dynamic fee based on balance
        FEE_PER_BYTE = smartFeeCalc(wallet_balance)
        print(f"Using fee rate: {FEE_PER_BYTE} sat/vB")
        
        # Estimate transaction size and fee
        estimated_tx_size = 250  # Approximate size in bytes for 1 input, 2 outputs
        fee_total = FEE_PER_BYTE * estimated_tx_size
        
        # Check if balance is too small for any transaction
        if wallet_balance <= fee_total:
            return f"Error: Balance too small for any transaction. Available: {wallet_balance/1e8:.8f} BTC, Minimum fee required: {fee_total/1e8:.8f} BTC"
        
        # Calculate amount to send (all balance minus fee)
        amount_to_send = wallet_balance - fee_total
        
        print(f"Sweeping wallet: {amount_to_send/1e8:.8f} BTC to {RECEIVER_ADDRESS}")
        print(f"Fee: {fee_total/1e8:.8f} BTC ({FEE_PER_BYTE} sat/vB)")
        
        # Create and send transaction
        tx = wallet.send_to(
            RECEIVER_ADDRESS,
            amount_to_send,
            fee=fee_total,
            min_confirms=0  # Allow unconfirmed UTXOs
        )
        
        if not tx:
            return "Error: Failed to create sweep transaction"
        
        tx_hex = tx.as_hex()
        if not tx_hex:
            return "Error: Failed to serialize transaction"
        
        print(f"Sweep transaction created successfully. Broadcasting...")
        result = broadcastTx(tx_hex)
        
        if result.startswith("Error") or result.startswith("Broadcast failed"):
            return result
        
        return f"Sweep transaction sent successfully! TXID: {result}. Sent: {amount_to_send/1e8:.8f} BTC"
        
    except Exception as e:
        print(f"Error in sweepBitcoin: {e}")
        return f"Error: Failed to sweep Bitcoin - {str(e)}"

def syncWalletAddress():
    """Sync the wallet address in config.json with the address that has funds"""
    try:
        wallet = getWalletInstance()
        if not wallet:
            return False
        
        wallet.scan()  # Rescan for UTXOs
        config_path = os.path.expanduser('~/TyWallet/config.json')
        
        # Find the address with the highest balance
        best_address = None
        best_balance = 0
        
        for key in wallet.keys():
            if key.balance > best_balance:
                best_balance = key.balance
                best_address = key.address
        
        # If no address has balance, use the main wallet address
        if not best_address:
            best_address = str(wallet.get_key().address)
            
        # Read current config
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if address needs updating
        config_address = data["addresses"].get("Bitcoin")
        if config_address != best_address:
            print(f"Address mismatch detected!")
            print(f"Config address: {config_address}")
            print(f"Best wallet address (with balance): {best_address}")
            print(f"Balance on this address: {best_balance/1e8:.8f} BTC")
            print(f"Updating config...")
            
            # Update config with address that has funds
            data["addresses"]["Bitcoin"] = best_address
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            print(f"Config updated with funded address: {best_address}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error syncing wallet address: {e}")
        return False