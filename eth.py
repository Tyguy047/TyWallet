import requests
import time
from web3 import Web3
from eth_account import Account
import os
import json

def priceGrab():
    try:
        url = 'https://api.tywallet.xyz/prices/ethereum'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return "Error: Price data could not be fetched!"

def walletGen():
    try:
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

        print("Ethereum mainnet wallet created successfully!")
        
        return {
            "Private_Key": account.key.hex(),
            "Public_Key": account.address,
            "Seed": mnemonic
        }
    except Exception as e:
        print(f"Error generating Ethereum wallet: {e}")
        return {"error": f"Failed to generate Ethereum wallet: {str(e)}"}

def balanceCheck():
    def addressGrab():
        try:
            with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data["addresses"].get("Ethereum")
        except Exception as e:
            print(f"Error reading Ethereum address from config: {e}")
            return None

    ADDRESS = addressGrab()
    
    # Validate address exists
    if not ADDRESS:
        return "Error: No Ethereum address configured!"
    
    # Validate address format
    if not ADDRESS.startswith('0x') or len(ADDRESS) != 42:
        return "Error: Invalid Ethereum address format!"

    print(f"Checking balance for address: {ADDRESS}")

    # Try multiple API endpoints for reliability - all free, no API key required
    api_endpoints = [
        {
            'name': 'Blockscout',
            'url': f"https://eth.blockscout.com/api?module=account&action=balance&address={ADDRESS}",
            'parser': lambda data: int(data['result']) / 1e18 if data.get('status') == '1' and data.get('result') else 0
        },
        {
            'name': 'Blockcypher',
            'url': f"https://api.blockcypher.com/v1/eth/main/addrs/{ADDRESS}/balance",
            'parser': lambda data: int(data.get('balance', 0)) / 1e18
        },
        {
            'name': 'Ethplorer',
            'url': f"https://api.ethplorer.io/getAddressInfo/{ADDRESS}?apiKey=freekey",
            'parser': lambda data: float(data.get('ETH', {}).get('balance', 0)) if isinstance(data.get('ETH'), dict) else 0
        }
    ]

    last_error = None
    
    for endpoint in api_endpoints:
        try:
            print(f"Trying {endpoint['name']}...")
            headers = {'User-Agent': 'TyWallet/1.0'}
            response = requests.get(endpoint['url'], timeout=15, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            print(f"Response from {endpoint['name']}: {data}")
            
            balance = endpoint['parser'](data)
            print(f"Parsed balance from {endpoint['name']}: {balance}")
            
            if balance is not None and balance >= 0:
                print(f"Returning balance: {balance:,.8f}")
                return f"{balance:,.8f}"
                
        except requests.RequestException as e:
            last_error = f"{endpoint['name']} network error: {e}"
            print(f"Failed to fetch balance from {endpoint['name']}: {e}")
            continue
        except (KeyError, ValueError, TypeError) as e:
            last_error = f"{endpoint['name']} data parsing error: {e}"
            print(f"Failed to parse balance from {endpoint['name']}: {e}")
            continue
        except Exception as e:
            last_error = f"{endpoint['name']} unexpected error: {e}"
            print(f"Unexpected error with {endpoint['name']}: {e}")
            continue

    # If all APIs fail, try Web3 RPC calls as last resort
    print("All APIs failed, trying RPC endpoints...")
    try:
        from web3 import Web3
        # Use a public RPC endpoint
        rpc_urls = [
            "https://rpc.ankr.com/eth",
            "https://ethereum.publicnode.com",
            "https://eth.llamarpc.com",
            "https://cloudflare-eth.com"
        ]
        
        for rpc_url in rpc_urls:
            try:
                print(f"Trying RPC: {rpc_url}")
                w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 15}))
                if w3.is_connected():
                    balance_wei = w3.eth.get_balance(ADDRESS)
                    balance_eth = w3.from_wei(balance_wei, 'ether')
                    print(f"RPC balance: {float(balance_eth):,.8f}")
                    return f"{float(balance_eth):,.8f}"
            except Exception as e:
                print(f"RPC {rpc_url} failed: {e}")
                continue
                
    except Exception as e:
        print(f"Web3 fallback failed: {e}")

    return f"Error: Could not fetch balance from any service. All APIs are currently unavailable. Last error: {last_error}"

def createTx(receiver, amount, gas_speed='normal'):

    def smartGas(speed='normal'):
        """
        Get smart gas price with user-friendly speed options
        speed options: 'slow', 'normal', 'fast'
        Enhanced with multiple fallback sources and realistic mainnet pricing
        """
        min_mainnet_gas = 12  # Minimum viable mainnet gas price in Gwei
        
        # Try multiple RPC endpoints for current gas price
        rpc_endpoints = [
            'https://ethereum.publicnode.com',
            'https://eth.drpc.org',
            'https://eth-mainnet.g.alchemy.com/v2/demo'
        ]
        
        current_gas_price_gwei = None
        
        for endpoint in rpc_endpoints:
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {
                    'jsonrpc': '2.0',
                    'method': 'eth_gasPrice',
                    'params': [],
                    'id': 1
                }
                response = requests.post(endpoint, json=payload, headers=headers, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        gas_price_wei = int(data['result'], 16)
                        current_gas_price_gwei = gas_price_wei / 1e9
                        # Ensure minimum viable price
                        current_gas_price_gwei = max(current_gas_price_gwei, min_mainnet_gas)
                        break
            except Exception:
                continue
        
        # If we got current gas price, calculate based on that
        if current_gas_price_gwei:
            multipliers = {'slow': 0.9, 'normal': 1.1, 'fast': 1.3}
            gas_price_gwei = current_gas_price_gwei * multipliers.get(speed, 1.1)
            # Ensure minimum and add buffer
            gas_price_gwei = max(gas_price_gwei, min_mainnet_gas)
            return int(gas_price_gwei * 1e9)
        
        # Try Etherscan API as fallback
        try:
            url = 'https://api.etherscan.io/api?module=gastracker&action=gasoracle'
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    result = data['result']
                    if speed == 'slow':
                        gas_price_gwei = float(result['SafeGasPrice'])
                    elif speed == 'fast':
                        gas_price_gwei = float(result['FastGasPrice'])
                    else:  # normal
                        gas_price_gwei = float(result['ProposeGasPrice'])
                    
                    # Validate and ensure minimum
                    gas_price_gwei = max(gas_price_gwei, min_mainnet_gas)
                    # Add reliability buffer
                    gas_price_gwei *= 1.15
                    
                    return int(gas_price_gwei * 1e9)
        except Exception:
            pass
        
        # Conservative fallback based on realistic mainnet conditions
        # These prices are based on typical mainnet usage patterns
        fallback_prices = {'slow': 18, 'normal': 25, 'fast': 35}
        gas_price_gwei = fallback_prices.get(speed, 25)
        return int(gas_price_gwei * 1e9)

    def getNonce(address):
        """Fetch the current nonce for the address from the network with multiple RPC fallbacks"""
        rpc_endpoints = [
            'https://ethereum.publicnode.com',
            'https://eth.drpc.org', 
            'https://eth-mainnet.g.alchemy.com/v2/demo',
            'https://cloudflare-eth.com'
        ]
        
        for endpoint in rpc_endpoints:
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getTransactionCount",
                    "params": [address, "latest"],
                    "id": 1
                }
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'result' in result:
                        return int(result['result'], 16)
            except Exception:
                continue
        
        # If all RPC endpoints fail, return 0 with warning
        print(f"Warning: Unable to fetch nonce for {address}, using 0")
        return 0

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
                print("Error: No Ethereum address found in config")
                return None
            
            wallet_file = os.path.expanduser("~/TyWallet/Ethereum_Wallet.json")
            if not os.path.exists(wallet_file):
                print(f"Error: Wallet file not found: {wallet_file}")
                return None
                
            with open(wallet_file, 'r') as f:
                wallet_data = json.load(f)
                
            if address not in wallet_data:
                print(f"Error: Address {address} not found in wallet file")
                print(f"Available addresses: {list(wallet_data.keys())}")
                return None
                
            return wallet_data[address]["Private_Key"]
        except Exception as e:
            print(f"Error retrieving private key: {e}")
            return None

    def validateWalletSetup():
        """Validate that the wallet is properly set up for transactions"""
        try:
            # Check if config exists and has Ethereum address
            address = addressGrab()
            if not address:
                return False, "No Ethereum address configured"
            
            # Check if wallet file exists
            wallet_file = os.path.expanduser("~/TyWallet/Ethereum_Wallet.json")
            if not os.path.exists(wallet_file):
                return False, "Ethereum wallet file not found. Please regenerate your wallet."
            
            # Check if private key exists for the configured address
            private_key = getPrivateKey()
            if not private_key:
                return False, f"Private key not found for address {address}. Wallet file may be corrupted."
            
            return True, "Wallet is properly configured"
        except Exception as e:
            return False, f"Wallet validation error: {e}"

    try:
        # Validate wallet setup first
        wallet_valid, wallet_message = validateWalletSetup()
        if not wallet_valid:
            return f"Error: {wallet_message}"
        
        # Validate inputs
        if not receiver or not amount:
            return "Error: Missing receiver address or amount"
        
        # Validate Ethereum address format
        if not validateEthereumAddress(receiver):
            return "Error: Invalid Ethereum address format"
            
        to_address = receiver
        tx_amount = float(amount)  # Amount in ETH
        
        # Validate amount
        if tx_amount <= 0:
            return "Error: Amount must be greater than 0"
        
        # Check if user has sufficient balance including fees
        sufficient, message = validateSufficientBalance(tx_amount)
        if not sufficient:
            return f"Error: {message}"
        
        fee = smartGas(gas_speed)  # Fetch gas price based on user's speed preference
        
        from_address = addressGrab()
        private_key = getPrivateKey()
        
        if not from_address or not private_key:
            return "Error: Unable to retrieve wallet information"
        
        # Get the current nonce for the sender address
        current_nonce = getNonce(from_address)
        
        # Create transaction with proper nonce
        tx = {
            'to': to_address,
            'value': int(tx_amount * 1e18),  # Convert ETH to Wei manually
            'gas': 21000,  # Standard gas limit for ETH transfer
            'gasPrice': fee,  # Gas price in wei from smartGas()
            'nonce': current_nonce,  # Use fetched nonce
            'chainId': 1,  # Ethereum mainnet chain ID
        }
        
        # Sign transaction offline
        w3 = Web3()  # Create Web3 instance without provider for offline signing
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        # Ensure the raw transaction has 0x prefix
        raw_tx_hex = signed_tx.raw_transaction.hex()
        if not raw_tx_hex.startswith('0x'):
            raw_tx_hex = '0x' + raw_tx_hex
            
        return raw_tx_hex
        
    except Exception as e:
        return f"Error creating transaction: {str(e)}"

def broadcastTx(TX):
    """Broadcast transaction with multiple RPC endpoint fallbacks"""
    # Ensure TX has 0x prefix
    if not TX.startswith('0x'):
        TX = '0x' + TX
    
    rpc_endpoints = [
        'https://ethereum.publicnode.com',
        'https://eth.drpc.org',
        'https://eth-mainnet.g.alchemy.com/v2/demo',
        'https://cloudflare-eth.com'
    ]
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": [TX],
        "id": 1
    }

    last_error = None
    
    for endpoint in rpc_endpoints:
        try:
            print(f"Broadcasting to {endpoint} with TX: {TX[:20]}...")  # Debug log
            response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result}")  # Debug log
                if 'result' in result:
                    return result['result']
                elif 'error' in result:
                    error_msg = result['error'].get('message', 'Unknown error')
                    print(f"RPC Error: {error_msg}")  # Debug log
                    # Skip to next endpoint for certain errors
                    if 'nonce too low' in error_msg.lower() or 'already known' in error_msg.lower():
                        last_error = error_msg
                        continue
                    return f"Transaction error: {error_msg}"
            last_error = f"HTTP {response.status_code}"
        except Exception as e:
            print(f"Exception with {endpoint}: {e}")  # Debug log
            last_error = str(e)
            continue

    return f"Error broadcasting transaction (tried all endpoints): {last_error}"

def getEthereumAddress():
    """Helper function to get the current Ethereum address"""
    try:
        with open(os.path.expanduser('~/TyWallet/config.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Ethereum")
    except Exception:
        return None

def validateEthereumAddress(address):
    """Validate if the provided string is a valid Ethereum address"""
    try:
        # Handle None and non-string inputs
        if address is None or not isinstance(address, str):
            return False
            
        # Handle empty string
        if not address.strip():
            return False
        
        # Remove whitespace
        address = address.strip().lower()
        
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Check if it's exactly 40 characters of valid hex
        if len(address) != 40:
            return False
            
        # Check if all characters are valid hex (0-9, a-f)
        int(address, 16)
        return True
    except (ValueError, TypeError, AttributeError):
        return False

def estimateTransactionFee():
    """Estimate the transaction fee in ETH for a standard ETH transfer"""
    try:
        # Use the same gas price logic as in createTx
        url = 'https://api.blockchair.com/ethereum/stats'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        gas_price_gwei = data['data']['avg_gas_price']
        gas_price_wei = int(gas_price_gwei * 1e9)
        
        gas_limit = 21000  # Standard gas limit for ETH transfer
        fee_wei = gas_price_wei * gas_limit
        fee_eth = fee_wei / 1e18
        return fee_eth
    except Exception:
        return 0.0004  # Fallback estimate (20 gwei * 21000 gas)

def validateSufficientBalance(amount):
    """Check if the user has sufficient balance for the transaction including fees"""
    try:
        # Get current balance
        current_balance_str = balanceCheck()
        if "error" in current_balance_str.lower():
            return False, "Unable to check balance"
        
        current_balance = float(current_balance_str.replace(',', ''))
        estimated_fee = estimateTransactionFee()
        total_needed = float(amount) + estimated_fee
        
        if current_balance < total_needed:
            return False, f"Insufficient balance. Need {total_needed:.8f} ETH (including fees), but have {current_balance:.8f} ETH"
        
        return True, "Sufficient balance"
    except Exception as e:
        return False, f"Error validating balance: {str(e)}"

def getTransactionDetails(tx_hash):
    """Get transaction details from the blockchain using transaction hash"""
    try:
        url = 'https://cloudflare-eth.com'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getTransactionByHash",
            "params": [tx_hash],
            "id": 1
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get('result', None)
    except Exception:
        return None

def formatWeiToEth(wei_amount):
    """Convert Wei to ETH with proper formatting"""
    try:
        eth_amount = int(wei_amount) / 1e18
        return f"{eth_amount:.8f}"
    except Exception:
        return "0.00000000"

def checkNetworkConnectivity():
    """Check if we can connect to Ethereum network with multiple endpoints"""
    test_endpoints = [
        'https://ethereum.publicnode.com',
        'https://eth.drpc.org',
        'https://eth-mainnet.g.alchemy.com/v2/demo'
    ]
    
    for endpoint in test_endpoints:
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    return True
        except Exception:
            continue
    return False

def getCurrentGasPrice():
    """Get current gas price in Gwei for display purposes with multiple sources"""
    # Try RPC endpoints first for most accurate current price
    rpc_endpoints = [
        'https://ethereum.publicnode.com',
        'https://eth.drpc.org',
        'https://eth-mainnet.g.alchemy.com/v2/demo'
    ]
    
    for endpoint in rpc_endpoints:
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                'jsonrpc': '2.0',
                'method': 'eth_gasPrice',
                'params': [],
                'id': 1
            }
            response = requests.post(endpoint, json=payload, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    gas_price_wei = int(data['result'], 16)
                    gas_price_gwei = gas_price_wei / 1e9
                    # Ensure minimum realistic mainnet price
                    return max(gas_price_gwei, 12)
        except Exception:
            continue
    
    # Fallback to APIs
    try:
        url = 'https://api.etherscan.io/api?module=gastracker&action=gasoracle'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1':
                gas_price = float(data['result']['ProposeGasPrice'])
                return max(gas_price, 12)
    except Exception:
        pass
    
    return 20  # Conservative fallback

def getEthereumStats():
    """Get general Ethereum network statistics"""
    try:
        url = 'https://api.blockchair.com/ethereum/stats'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        stats = data['data']
        return {
            "current_block": stats.get('blocks', 'Unknown'),
            "pending_transactions": stats.get('mempool_transactions', 'Unknown'),
            "avg_gas_price": stats.get('avg_gas_price', 'Unknown'),
            "network_hash_rate": stats.get('hashrate_24h', 'Unknown')
        }
    except Exception:
        return {
            "current_block": "Error",
            "pending_transactions": "Error", 
            "avg_gas_price": "Error",
            "network_hash_rate": "Error"
        }

def getGasFeeEstimates():
    """Get gas fee estimates in different speeds with USD costs - Enhanced with realistic pricing"""
    try:
        # Get ETH price for USD conversion
        eth_price_usd = float(priceGrab().replace(',', ''))
        
        estimates = {}
        speeds = ['slow', 'normal', 'fast']
        min_mainnet_gas = 12  # Minimum viable mainnet gas price
        
        # Get current gas price from RPC for more accurate base pricing
        current_gas_gwei = getCurrentGasPrice()
        
        for speed in speeds:
            try:
                # Calculate gas price based on current network conditions
                if speed == 'slow':
                    gas_price_gwei = max(current_gas_gwei * 0.9, min_mainnet_gas)
                elif speed == 'fast':
                    gas_price_gwei = current_gas_gwei * 1.3
                else:  # normal
                    gas_price_gwei = current_gas_gwei * 1.1
                
                # Ensure minimum and apply safety buffer
                gas_price_gwei = max(gas_price_gwei, min_mainnet_gas)
                
                # Try to get more accurate estimates from APIs
                try:
                    url = 'https://api.etherscan.io/api?module=gastracker&action=gasoracle'
                    response = requests.get(url, timeout=8)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == '1':
                            result = data['result']
                            api_price = 0
                            if speed == 'slow':
                                api_price = float(result['SafeGasPrice'])
                            elif speed == 'fast':
                                api_price = float(result['FastGasPrice'])
                            else:  # normal
                                api_price = float(result['ProposeGasPrice'])
                            
                            # Use API price if it's reasonable, otherwise use calculated price
                            if api_price >= min_mainnet_gas:
                                gas_price_gwei = max(api_price * 1.1, min_mainnet_gas)  # 10% buffer
                except Exception:
                    pass
                
                # Calculate fee in ETH and USD
                gas_limit = 21000  # Standard ETH transfer
                fee_wei = int(gas_price_gwei * 1e9) * gas_limit
                fee_eth = fee_wei / 1e18
                fee_usd = fee_eth * eth_price_usd
                
                estimates[speed] = {
                    'gas_price_gwei': gas_price_gwei,
                    'fee_eth': fee_eth,
                    'fee_usd': fee_usd,
                    'estimated_time': {
                        'slow': '5-10 minutes',
                        'normal': '2-5 minutes', 
                        'fast': '30 seconds - 2 minutes'
                    }[speed]
                }
                
            except Exception:
                # Enhanced fallback estimates based on realistic mainnet conditions
                fallback_gwei = {'slow': 18, 'normal': 25, 'fast': 35}[speed]
                fee_eth = (fallback_gwei * 21000) / 1e9
                estimates[speed] = {
                    'gas_price_gwei': fallback_gwei,
                    'fee_eth': fee_eth,
                    'fee_usd': fee_eth * eth_price_usd,
                    'estimated_time': {
                        'slow': '5-10 minutes',
                        'normal': '2-5 minutes',
                        'fast': '30 seconds - 2 minutes'
                    }[speed]
                }
        
        return estimates
        
    except Exception:
        # Complete fallback with realistic mainnet prices
        return {
            'slow': {'gas_price_gwei': 18, 'fee_eth': 0.000378, 'fee_usd': 1.05, 'estimated_time': '5-10 minutes'},
            'normal': {'gas_price_gwei': 25, 'fee_eth': 0.000525, 'fee_usd': 1.46, 'estimated_time': '2-5 minutes'},
            'fast': {'gas_price_gwei': 35, 'fee_eth': 0.000735, 'fee_usd': 2.04, 'estimated_time': '30 seconds - 2 minutes'}
        }

def getNetworkCongestionLevel():
    """Get network congestion level and recommendations"""
    try:
        stats = getEthereumStats()
        gas_price = getCurrentGasPrice()
        
        # Determine congestion level based on gas price
        if gas_price < 20:
            congestion = "Low"
            recommendation = "Great time to transact! Low fees."
            color = "green"
        elif gas_price < 50:
            congestion = "Moderate"
            recommendation = "Normal network activity. Standard fees."
            color = "orange"
        else:
            congestion = "High"
            recommendation = "Network is congested. Consider waiting or using fast speed."
            color = "red"
            
        return {
            "level": congestion,
            "recommendation": recommendation,
            "color": color,
            "gas_price": gas_price,
            "pending_transactions": stats.get("pending_transactions", "Unknown")
        }
    except Exception:
        return {
            "level": "Unknown",
            "recommendation": "Unable to determine network conditions",
            "color": "gray",
            "gas_price": "Unknown",
            "pending_transactions": "Unknown"
        }

def getOptimalGasSpeed(urgency="normal"):
    """Get optimal gas speed based on current network conditions and user urgency"""
    try:
        congestion = getNetworkCongestionLevel()
        gas_price = congestion["gas_price"]
        
        if urgency == "urgent":
            return "fast"
        elif urgency == "economy" or gas_price > 50:
            return "slow"
        else:
            return "normal"
    except Exception:
        return "normal"

def estimateTransactionTime(gas_speed):
    """Estimate transaction confirmation time based on current network conditions"""
    try:
        congestion = getNetworkCongestionLevel()
        base_times = {
            "slow": (300, 600),    # 5-10 minutes
            "normal": (120, 300),  # 2-5 minutes  
            "fast": (30, 120)     # 30 seconds - 2 minutes
        }
        
        min_time, max_time = base_times.get(gas_speed, (120, 300))
        
        # Adjust based on congestion
        if congestion["level"] == "High":
            min_time *= 1.5
            max_time *= 2
        elif congestion["level"] == "Low":
            min_time *= 0.7
            max_time *= 0.8
            
        return f"{int(min_time//60)}-{int(max_time//60)} minutes"
    except Exception:
        return {
            "slow": "5-10 minutes",
            "normal": "2-5 minutes",
            "fast": "30 seconds - 2 minutes"
        }.get(gas_speed, "2-5 minutes")

def formatTransactionSummary(to_address, amount, gas_speed):
    """Create a formatted transaction summary for user confirmation"""
    try:
        estimates = getGasFeeEstimates()
        estimate = estimates[gas_speed]
        congestion = getNetworkCongestionLevel()
        
        return f"""
Transaction Summary:
├─ To: {to_address[:10]}...{to_address[-8:]}
├─ Amount: {amount} ETH
├─ Fee: {estimate['fee_eth']:.6f} ETH (${estimate['fee_usd']:.2f})
├─ Total: {float(amount) + estimate['fee_eth']:.6f} ETH
├─ Speed: {gas_speed.title()}
├─ Est. Time: {estimate['estimated_time']}
└─ Network: {congestion['level']} congestion
        """
    except Exception:
        return f"Amount: {amount} ETH\nRecipient: {to_address}"

# Add comprehensive transaction validation and monitoring utilities

def validateTransactionParameters(to_address, amount, gas_speed='normal'):
    """Comprehensive validation of transaction parameters before creation"""
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate address
    if not validateEthereumAddress(to_address):
        validation_results['valid'] = False
        validation_results['errors'].append("Invalid Ethereum address format")
    
    # Validate amount
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            validation_results['valid'] = False
            validation_results['errors'].append("Amount must be greater than 0")
        elif amount_float < 0.000001:  # Less than 1 Gwei equivalent
            validation_results['warnings'].append("Very small amount - double check this is correct")
    except (ValueError, TypeError):
        validation_results['valid'] = False
        validation_results['errors'].append("Invalid amount format")
    
    # Validate gas speed
    if gas_speed not in ['slow', 'normal', 'fast']:
        validation_results['warnings'].append("Unknown gas speed, using 'normal'")
    
    # Check network connectivity
    if not checkNetworkConnectivity():
        validation_results['valid'] = False
        validation_results['errors'].append("Unable to connect to Ethereum network")
    
    # Check balance if possible
    try:
        sufficient, message = validateSufficientBalance(amount_float)
        if not sufficient:
            validation_results['valid'] = False
            validation_results['errors'].append(message)
    except Exception as e:
        validation_results['warnings'].append(f"Unable to verify balance: {str(e)}")
    
    return validation_results

def getTransactionStatus(tx_hash):
    """Get the status of a transaction by hash with multiple RPC fallbacks"""
    rpc_endpoints = [
        'https://ethereum.publicnode.com',
        'https://eth.drpc.org',
        'https://eth-mainnet.g.alchemy.com/v2/demo'
    ]
    
    for endpoint in rpc_endpoints:
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [tx_hash],
                "id": 1
            }
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and result['result']:
                    receipt = result['result']
                    status = int(receipt.get('status', '0x0'), 16)
                    return {
                        'confirmed': True,
                        'success': status == 1,
                        'block_number': int(receipt.get('blockNumber', '0x0'), 16),
                        'gas_used': int(receipt.get('gasUsed', '0x0'), 16),
                        'transaction_fee': int(receipt.get('gasUsed', '0x0'), 16) * int(receipt.get('effectiveGasPrice', '0x0'), 16) / 1e18
                    }
                elif 'result' in result and result['result'] is None:
                    return {'confirmed': False, 'pending': True}
        except Exception:
            continue
    
    return {'error': 'Unable to check transaction status'}

def estimateOptimalGasPrice():
    """Estimate optimal gas price based on current network conditions"""
    try:
        current_gas = getCurrentGasPrice()
        congestion = getNetworkCongestionLevel()
        
        # Adjust based on congestion
        if congestion['level'] == 'High':
            optimal_gas = current_gas * 1.2
        elif congestion['level'] == 'Low':
            optimal_gas = current_gas * 0.9
        else:
            optimal_gas = current_gas
        
        # Ensure minimum viable price
        optimal_gas = max(optimal_gas, 12)
        
        return {
            'optimal_gas_gwei': optimal_gas,
            'current_gas_gwei': current_gas,
            'congestion_level': congestion['level'],
            'recommendation': f"Recommended gas price: {optimal_gas:.1f} Gwei"
        }
    except Exception:
        return {
            'optimal_gas_gwei': 20,
            'current_gas_gwei': 20,
            'congestion_level': 'Unknown',
            'recommendation': "Recommended gas price: 20 Gwei (fallback)"
        }

def createTransactionWithValidation(receiver, amount, gas_speed='normal'):
    """Enhanced transaction creation with comprehensive validation"""
    # Pre-validation
    validation = validateTransactionParameters(receiver, amount, gas_speed)
    if not validation['valid']:
        return {
            'success': False,
            'error': '; '.join(validation['errors']),
            'warnings': validation['warnings']
        }
    
    # Create transaction
    try:
        raw_tx = createTx(receiver, amount, gas_speed)
        if raw_tx.startswith('Error'):
            return {
                'success': False,
                'error': raw_tx,
                'warnings': validation['warnings']
            }
        
        return {
            'success': True,
            'raw_transaction': raw_tx,
            'warnings': validation['warnings'],
            'transaction_summary': formatTransactionSummary(receiver, amount, gas_speed)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Transaction creation failed: {str(e)}",
            'warnings': validation['warnings']
        }

def monitorPendingTransaction(tx_hash, timeout_minutes=10):
    """Monitor a pending transaction until confirmation or timeout"""
    import time
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    check_interval = 30  # Check every 30 seconds
    
    while time.time() - start_time < timeout_seconds:
        status = getTransactionStatus(tx_hash)
        
        if status.get('confirmed'):
            return {
                'status': 'confirmed',
                'success': status.get('success', False),
                'block_number': status.get('block_number'),
                'gas_used': status.get('gas_used'),
                'transaction_fee': status.get('transaction_fee')
            }
        elif status.get('error'):
            return {
                'status': 'error',
                'message': status['error']
            }
        
        time.sleep(check_interval)
    
    return {
        'status': 'timeout',
        'message': f'Transaction not confirmed within {timeout_minutes} minutes'
    }

def getEthereumAddressInfo():
    """Get comprehensive information about the current Ethereum address"""
    try:
        address = getEthereumAddress()
        if not address:
            return {
                'address': None,
                'error': 'No Ethereum address configured'
            }
        
        # Get balance
        balance_str = balanceCheck()
        balance_eth = 0.0
        if not balance_str.startswith('An error'):
            try:
                balance_eth = float(balance_str.replace(',', ''))
            except ValueError:
                pass
        
        # Get USD value
        try:
            eth_price = float(priceGrab().replace(',', ''))
            balance_usd = balance_eth * eth_price
        except Exception:
            balance_usd = 0.0
        
        return {
            'address': address,
            'balance_eth': balance_eth,
            'balance_usd': balance_usd,
            'formatted_address': f"{address[:6]}...{address[-4:]}",
            'network_connected': checkNetworkConnectivity()
        }
    except Exception as e:
        return {
            'address': None,
            'error': f'Failed to get address info: {str(e)}'
        }

def getRecommendedGasSettings():
    """Get recommended gas settings based on current network conditions"""
    try:
        congestion = getNetworkCongestionLevel()
        optimal = estimateOptimalGasPrice()
        estimates = getGasFeeEstimates()
        
        # Determine recommended speed based on conditions
        if congestion['level'] == 'High':
            recommended_speed = 'fast'
            reason = 'Network is congested - fast speed recommended for timely confirmation'
        elif congestion['level'] == 'Low':
            recommended_speed = 'slow'
            reason = 'Network is quiet - slow speed offers good value'
        else:
            recommended_speed = 'normal'
            reason = 'Normal network conditions - standard speed is optimal'
        
        return {
            'recommended_speed': recommended_speed,
            'reason': reason,
            'congestion_level': congestion['level'],
            'optimal_gas_price': optimal['optimal_gas_gwei'],
            'estimates': estimates
        }
    except Exception as e:
        return {
            'recommended_speed': 'normal',
            'reason': 'Unable to analyze network conditions',
            'error': str(e)
        }

def formatGasSpeedComparison():
    """Format gas speed comparison for user interface"""
    try:
        estimates = getGasFeeEstimates()
        comparison = []
        
        for speed in ['slow', 'normal', 'fast']:
            if speed in estimates:
                data = estimates[speed]
                comparison.append({
                    'speed': speed.title(),
                    'gas_price': f"{data['gas_price_gwei']:.1f} Gwei",
                    'fee_eth': f"{data['fee_eth']:.6f} ETH",
                    'fee_usd': f"${data['fee_usd']:.2f}",
                    'time': data['estimated_time'],
                    'description': {
                        'slow': 'Economical - Best for non-urgent transactions',
                        'normal': 'Balanced - Good speed and reasonable cost',
                        'fast': 'Priority - Quick confirmation, higher cost'
                    }[speed]
                })
        
        return comparison
    except Exception:
        return [
            {'speed': 'Slow', 'gas_price': '18 Gwei', 'fee_eth': '0.000378 ETH', 'fee_usd': '$1.05', 'time': '5-10 minutes', 'description': 'Economical option'},
            {'speed': 'Normal', 'gas_price': '25 Gwei', 'fee_eth': '0.000525 ETH', 'fee_usd': '$1.46', 'time': '2-5 minutes', 'description': 'Balanced option'},
            {'speed': 'Fast', 'gas_price': '35 Gwei', 'fee_eth': '0.000735 ETH', 'fee_usd': '$2.04', 'time': '30s-2 minutes', 'description': 'Priority option'}
        ]

def createAdvancedTransactionSummary(to_address, amount, gas_speed):
    """Create advanced transaction summary with all relevant information"""
    try:
        estimates = getGasFeeEstimates()
        if gas_speed not in estimates:
            gas_speed = 'normal'
        
        estimate = estimates[gas_speed]
        congestion = getNetworkCongestionLevel()
        address_info = getEthereumAddressInfo()
        
        total_cost = float(amount) + estimate['fee_eth']
        
        summary = {
            'from_address': address_info.get('address', 'Unknown'),
            'to_address': to_address,
            'amount_eth': float(amount),
            'gas_speed': gas_speed,
            'gas_price_gwei': estimate['gas_price_gwei'],
            'fee_eth': estimate['fee_eth'],
            'fee_usd': estimate['fee_usd'],
            'total_cost_eth': total_cost,
            'total_cost_usd': total_cost * float(priceGrab().replace(',', '')),
            'estimated_time': estimate['estimated_time'],
            'network_congestion': congestion['level'],
            'current_balance': address_info.get('balance_eth', 0),
            'remaining_balance': address_info.get('balance_eth', 0) - total_cost,
            'sufficient_balance': address_info.get('balance_eth', 0) >= total_cost
        }
        
        return summary
    except Exception as e:
        return {'error': f'Failed to create transaction summary: {str(e)}'}