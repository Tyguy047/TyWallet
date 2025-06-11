# Packages
from PySide6.QtWidgets import QMessageBox, QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, QObject, Signal
import sys
import os
import json
from cryptography.fernet import Fernet
import threading

# Coins
import btc
import eth
import xmr

app = None
window = None
layout = None
config_dir = os.path.expanduser('~/TyWallet')
config_path = os.path.join(config_dir, 'config.json')



def getName():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["general"].get("Name", "User")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return "User"

def getFaveCoin():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["general"].get("FaveCoin", "")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return ""

def checkBitcoinWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["coins"].get("Bitcoin")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return False

def checkMoneroWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["coins"].get("Monero")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return False

def checkEthereumWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            result = data["coins"].get("Ethereum")
            return result
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return False

def getBitcoinWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Bitcoin")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return ""

def getMoneroWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Monero")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return ""

def getEthereumWallet():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["addresses"].get("Ethereum")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return ""

def startUp():
    global app, window, layout

    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("TyWallet")
    window.resize(600, 400)

    layout = QVBoxLayout()
    window.setLayout(layout)
    window.show()

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    wallets_dir = os.path.expanduser('~/TyWallet/Wallets')
    if not os.path.exists(wallets_dir):
        os.makedirs(wallets_dir)

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as config:
            json.dump({
                "coins": {
                    "Bitcoin": False,
                    "Monero": False,
                    "Ethereum": False,
                },

                "addresses": {
                    "Bitcoin": {},
                    "Monero": {},
                    "Ethereum": {},
                },
                "general": {
                    "Name": "User",
                    "FaveCoin": "Your Favorite Coin",
                    "CMC_API": False,

                }
            },
            config, indent=4)
        initStart()

    else:
        menuScreen()

def setWindow():
    global layout
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

def initStart():
    setWindow()

    def title():
        title = QLabel("Let get to know a few things about you...")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()

    def setConfigs():

        def saveName():
            name = name_input.text()
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["general"]["Name"] = name
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            menuScreen()

        def faveBitcoin():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["general"]["FaveCoin"] = "Bitcoin"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        def faveMonero():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["general"]["FaveCoin"] = "Monero"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        def faveEthereum():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["general"]["FaveCoin"] = "Ethereum"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()


        input_label = QLabel("Enter your name:")
        input_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(input_label)

        name_input = QLineEdit()
        name_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_input)

        btc_button = QPushButton("Bitcoin")
        layout.addWidget(btc_button)
        btc_button.clicked.connect(faveBitcoin)

        xmr_button = QPushButton("Monero")
        layout.addWidget(xmr_button)
        xmr_button.clicked.connect(faveMonero)
        

        eth_button = QPushButton("Ethereum")
        layout.addWidget(eth_button)
        eth_button.clicked.connect(faveEthereum)

        submit_btn = QPushButton("Start Your Legendary Journey With TyWallet...")
        layout.addWidget(submit_btn)
        submit_btn.clicked.connect(saveName)
    setConfigs()

def menuScreen():
    setWindow()

    NAME = getName()
    FAVE_COIN = getFaveCoin()

    def title():
        display_name = NAME if NAME else "User"
        if FAVE_COIN:
            subtitle = f"Have you checked up on {FAVE_COIN} yet today?"
        else:
            subtitle = "Set your favorite coin to get started!"
        title = QLabel(f"""<html>
<b>Hey {display_name}, welcome back to TyWallet!</b><br>
<i>{subtitle}</i>
</html>""")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()

    def cryptoPrices():
        try:
            BTC_PRICE = btc.priceGrab()
            MONERO_PRICE = xmr.priceGrab()
            ETH_PRICE = eth.priceGrab()
        except Exception:
            BTC_PRICE = "Error: Price data could not be fetched!"
            MONERO_PRICE = "Error: Price data could not be fetched!"
            ETH_PRICE = "Error: Price data could not be fetched!"

        price = QLabel(f"""<html>Bitcoin: ${BTC_PRICE}<br>
        Monero: ${MONERO_PRICE}<br>
        Ethereum: ${ETH_PRICE}<br><br>
        <i>Price data from our own API: <a href="https://api.tywallet.xyz">https://api.tywallet.xyz</a></i>
        <html>
        """)
        price.setOpenExternalLinks(True)
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    cryptoPrices()

    def options():
        # Use your wallets
        def bitcoinMenu():
            bitcoin = QPushButton("Bitcoin Menu")
            bitcoin.clicked.connect(bitcoinScreen)
            layout.addWidget(bitcoin)

        # Make new wallets
        def makeBitcoinWallet():
            def generateWallet():
                WALLET_GEN = btc.walletGen()
                
                # Check if wallet generation failed
                if "error" in WALLET_GEN:
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Error")
                    error_popup.setText(f"Failed to generate Bitcoin wallet:\n{WALLET_GEN['error']}")
                    error_popup.exec()
                    return
                
                SEED = WALLET_GEN["Seed"]
                ADDRESS = WALLET_GEN["Address"]
                
                with open(config_path, 'r+', encoding='utf-8') as config:
                    data = json.load(config)
                    data["coins"]["Bitcoin"] = True
                    data["addresses"]["Bitcoin"] = ADDRESS
                    config.seek(0)
                    json.dump(data, config, indent=4)
                    config.truncate()
                success_popup = QMessageBox()
                success_popup.setWindowTitle("Success")
                success_popup.setText(f"""<html><center>
<b>Wallet successfully generated!</b><br><br>
<i>Write your seed phrase down somewhere safe incase you need to recover your wallet:</i><br><br><br>
{SEED}
</center>
</html>""")
                success_popup.setStandardButtons(QMessageBox.Ok)
                success_popup.buttonClicked.connect(lambda: menuScreen())
                success_popup.exec()
            make_wallet = QPushButton("Make A Bitcoin Wallet")
            make_wallet.clicked.connect(generateWallet)
            layout.addWidget(make_wallet)

        def moneroMenu():
            monero = QPushButton("Monero Menu")
            monero.clicked.connect(lambda: QMessageBox.information(window, "Coming Soon", "Monero functionality is coming soon!"))
            layout.addWidget(monero)

        def makeMoneroWallet():
            make_monero_wallet = QPushButton("Make A Monero Wallet")
            make_monero_wallet.clicked.connect(lambda: QMessageBox.information(window, "Coming Soon", "Monero wallet generation is coming soon!"))
            layout.addWidget(make_monero_wallet)

        def ethereumMenu():
            ethereum = QPushButton("Ethereum Menu")
            ethereum.clicked.connect(ethereumScreen)
            layout.addWidget(ethereum)

        def makeEthereumWallet():
            def generateEthWallet():
                try:
                    WALLET = eth.walletGen()
                    
                    # Check if wallet generation failed
                    if "error" in str(WALLET).lower() or not WALLET or not WALLET.get("Public_Key"):
                        error_popup = QMessageBox()
                        error_popup.setWindowTitle("Error")
                        error_popup.setText(f"Failed to generate Ethereum wallet. Please try again.")
                        error_popup.exec()
                        return

                    with open(config_path, 'r+', encoding='utf-8') as config:
                        data = json.load(config)
                        data["coins"]["Ethereum"] = True
                        data["addresses"]["Ethereum"] = WALLET["Public_Key"]
                        config.seek(0)
                        json.dump(data, config, indent=4)
                        config.truncate()
                    success_popup = QMessageBox()
                    success_popup.setWindowTitle("Success")
                    success_popup.setText(f"""<html><center>
<b>Wallet successfully generated!</b><br><br>
<i>Write your seed phrase down somewhere safe incase you need to recover your wallet:</i><br><br><br>
{WALLET["Seed"]}
</center>
</html>""")
                    success_popup.setStandardButtons(QMessageBox.Ok)
                    success_popup.buttonClicked.connect(lambda: menuScreen())
                    success_popup.exec()
                except Exception as e:
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Error")
                    error_popup.setText(f"Failed to generate Ethereum wallet:\n{str(e)}")
                    error_popup.exec()
            
            make_eth_wallet = QPushButton("Make An Ethereum Wallet")
            make_eth_wallet.clicked.connect(generateEthWallet)
            layout.addWidget(make_eth_wallet)

        if not checkBitcoinWallet():
            makeBitcoinWallet()
        else:
            bitcoinMenu()

        if not checkMoneroWallet():
            makeMoneroWallet()
        else:
            moneroMenu()

        if not checkEthereumWallet():
            makeEthereumWallet()
        else:
            ethereumMenu()
    options()

def bitcoinScreen():
    setWindow()

    def title():
        title = QLabel("Bitcoin")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()

    def balance():
        try:
            BTC_BALANCE = btc.balanceCheck()
            if isinstance(BTC_BALANCE, dict):
                CONFIRMED = BTC_BALANCE["confirmed_balance"]
                PENDING = BTC_BALANCE["unconfirmed_balance"]
                
                balance_text = f"""<html>
<b>Bitcoin Balance</b><br><br>
Confirmed Balance: <b>{CONFIRMED} BTC</b><br>
Pending Balance: <b>{PENDING} BTC</b><br><br>
<i>Pending funds are still processing and cannot be spent yet!<br>
If your unconfirmed balance is negative, it means you have an outgoing transaction.</i>
</html>"""
            else:
                # Handle error case
                balance_text = f"""<html>
<b>Bitcoin Balance</b><br><br>
<i style="color: red;">{BTC_BALANCE}</i>
</html>"""
                
            balance_label = QLabel(balance_text)
            balance_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(balance_label)
        except Exception as e:
            error_label = QLabel(f"""<html>
<b>Bitcoin Balance</b><br><br>
<i style="color: red;">Error loading balance: {str(e)}</i>
</html>""")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
    
    balance()

    def price():
        BTC_PRICE = btc.priceGrab()

        price = QLabel(f"""<html>
${BTC_PRICE}
</html>""")
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    price()

    def sendBitcoin():
        receiver_label = QLabel("Enter the Bitcoin address of who will be receiving the fund you wish to send")
        receiver_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_label)

        receiver_input = QLineEdit()
        receiver_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_input)

        amount_label = QLabel("Enter the amount of BTC you would like to send")
        amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_label)

        amount_input = QLineEdit()
        amount_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_input)

        send_button = QPushButton("Send Transaction")

        def on_send_click():
            receiver = receiver_input.text().strip()
            amount_text = amount_input.text().strip()
            if not receiver:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText("Please enter a valid receiver address.")
                error_popup.exec()
                return
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText("Please enter a valid positive amount.")
                error_popup.exec()
                return
            try:
                tx_result = btc.sendBitcoin(receiver, amount)
                
                # Check if it's an error message
                if tx_result.startswith("Error:") or tx_result.startswith("Network error:"):
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Transaction Failed")
                    error_popup.setText(tx_result)
                    error_popup.exec()
                else:
                    success_popup = QMessageBox()
                    success_popup.setWindowTitle("Transaction Sent")
                    success_popup.setText(tx_result)
                    success_popup.exec()
            except Exception as e:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText(f"Failed to send transaction:\n{str(e)}")
                error_popup.exec()

        send_button.clicked.connect(on_send_click)
        layout.addWidget(send_button)
        
        # Add sweep button for small balances
        sweep_button = QPushButton("Send Maximum Amount (Sweep Wallet)")
        
        def on_sweep_click():
            receiver = receiver_input.text().strip()
            if not receiver:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText("Please enter a valid receiver address.")
                error_popup.exec()
                return
            
            # Confirm sweep action
            confirm_popup = QMessageBox()
            confirm_popup.setWindowTitle("Confirm Sweep")
            confirm_popup.setText(f"This will send ALL available Bitcoin (minus transaction fees) to:\n{receiver}\n\nAre you sure?")
            confirm_popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirm_popup.setDefaultButton(QMessageBox.StandardButton.No)
            
            if confirm_popup.exec() == QMessageBox.StandardButton.Yes:
                try:
                    tx_result = btc.sweepBitcoin(receiver)
                    
                    # Check if it's an error message
                    if tx_result.startswith("Error:") or tx_result.startswith("Network error:"):
                        error_popup = QMessageBox()
                        error_popup.setWindowTitle("Sweep Failed")
                        error_popup.setText(tx_result)
                        error_popup.exec()
                    else:
                        success_popup = QMessageBox()
                        success_popup.setWindowTitle("Sweep Successful")
                        success_popup.setText(tx_result)
                        success_popup.exec()
                except Exception as e:
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Error")
                    error_popup.setText(f"Failed to sweep wallet:\n{str(e)}")
                    error_popup.exec()
        
        sweep_button.clicked.connect(on_sweep_click)
        layout.addWidget(sweep_button)
    sendBitcoin()

    def address():
        BTC_ADDRESS = getBitcoinWallet()

        address = QLabel(f"""<html>
Your Bitcoin Address Is: {BTC_ADDRESS}
</html>""")
        address.setAlignment(Qt.AlignCenter)
        layout.addWidget(address)

        copy_button = QPushButton("Copy Address To Clipboard")
        def copyButton():
            clipboard = QApplication.clipboard()
            clipboard.setText(BTC_ADDRESS)
        copy_button.clicked.connect(copyButton)
        layout.addWidget(copy_button)
    address()

    def backToMenu():
        back = QPushButton("Back To Menu")
        back.clicked.connect(menuScreen)
        layout.addWidget(back)
    backToMenu()

def ethereumScreen():
    setWindow()
    
    def title():
        title = QLabel("Ethereum")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()

    def balance():
        try:
            ETH_BALANCE = eth.balanceCheck()
            
            # Check if it's an error message
            if ETH_BALANCE.startswith("Error:"):
                balance_text = f"""<html>
<b>Ethereum Balance</b><br><br>
<i style="color: red;">{ETH_BALANCE}</i>
</html>"""
            else:
                # Parse the balance to show it nicely
                try:
                    balance_float = float(ETH_BALANCE.replace(',', ''))
                    if balance_float == 0:
                        balance_display = "0.00000000"
                        status_text = "<i>Your wallet is empty. You can receive ETH at the address shown below.</i>"
                    else:
                        balance_display = f"{balance_float:,.8f}"
                        status_text = "<i>Available for transactions</i>"
                    
                    balance_text = f"""<html>
<b>Ethereum Balance</b><br><br>
<b>{balance_display} ETH</b><br><br>
{status_text}
</html>"""
                except ValueError:
                    # Fallback if parsing fails
                    balance_text = f"""<html>
<b>Ethereum Balance</b><br><br>
<b>{ETH_BALANCE} ETH</b>
</html>"""
            
            balance_label = QLabel(balance_text)
            balance_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(balance_label)
        except Exception as e:
            error_label = QLabel(f"""<html>
<b>Ethereum Balance</b><br><br>
<i style="color: red;">Error loading balance: {str(e)}</i>
</html>""")
            error_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(error_label)
    balance()

    def price():
        ETH_PRICE = eth.priceGrab()

        price = QLabel(f"""<html>
<b>Current ETH Price: ${ETH_PRICE}</b>
</html>""")
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    price()
    
    def gasInfo():
        """Display current gas price information"""
        try:
            current_gas = eth.getCurrentGasPrice()
            estimates = eth.getGasFeeEstimates()
            
            gas_info_text = f"""<html>
<b>Current Network Conditions:</b><br>
Average Gas Price: {current_gas} Gwei<br><br>
<b>Transaction Fee Estimates:</b><br>
🐌 Slow: {estimates['slow']['fee_eth']:.6f} ETH (${estimates['slow']['fee_usd']:.2f}) - {estimates['slow']['estimated_time']}<br>
⚡ Normal: {estimates['normal']['fee_eth']:.6f} ETH (${estimates['normal']['fee_usd']:.2f}) - {estimates['normal']['estimated_time']}<br>
🚀 Fast: {estimates['fast']['fee_eth']:.6f} ETH (${estimates['fast']['fee_usd']:.2f}) - {estimates['fast']['estimated_time']}
</html>"""
            
            gas_info = QLabel(gas_info_text)
            gas_info.setAlignment(Qt.AlignCenter)
            layout.addWidget(gas_info)
        except Exception:
            gas_info = QLabel("Gas price information temporarily unavailable")
            gas_info.setAlignment(Qt.AlignCenter)
            layout.addWidget(gas_info)
    gasInfo()

    def sendEthereum():
        from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout
        
        receiver_label = QLabel("Enter the Ethereum address of who will be receiving the fund you wish to send")
        receiver_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_label)

        receiver_input = QLineEdit()
        receiver_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_input)

        amount_label = QLabel("Enter the amount of ETH you would like to send")
        amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_label)

        amount_input = QLineEdit()
        amount_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_input)

        # Gas Speed Selection
        gas_group = QGroupBox("Transaction Speed & Fee")
        gas_layout = QVBoxLayout()
        
        gas_speed_label = QLabel("Select transaction speed:")
        gas_layout.addWidget(gas_speed_label)
        
        gas_speed_combo = QComboBox()
        gas_speed_combo.addItems(["Slow (Cheapest)", "Normal (Recommended)", "Fast (Urgent)"])
        gas_speed_combo.setCurrentIndex(1)  # Default to Normal
        gas_layout.addWidget(gas_speed_combo)
        
        # Fee estimate display
        fee_estimate_label = QLabel("Estimated fee: Calculating...")
        fee_estimate_label.setAlignment(Qt.AlignCenter)
        gas_layout.addWidget(fee_estimate_label)
        
        gas_group.setLayout(gas_layout)
        layout.addWidget(gas_group)
        
        def updateFeeEstimate():
            """Update fee estimate when gas speed changes"""
            try:
                estimates = eth.getGasFeeEstimates()
                speed_map = {0: 'slow', 1: 'normal', 2: 'fast'}
                selected_speed = speed_map[gas_speed_combo.currentIndex()]
                estimate = estimates[selected_speed]
                
                fee_text = f"""<html>
<b>Estimated fee: {estimate['fee_eth']:.6f} ETH (${estimate['fee_usd']:.2f})</b><br>
<i>Gas price: {estimate['gas_price_gwei']:.1f} Gwei</i><br>
<i>Expected time: {estimate['estimated_time']}</i>
</html>"""
                fee_estimate_label.setText(fee_text)
            except Exception:
                fee_estimate_label.setText("Fee estimate: ~0.0004 ETH")
        
        # Update fee estimate when selection changes
        gas_speed_combo.currentIndexChanged.connect(updateFeeEstimate)
        # Initial fee estimate
        updateFeeEstimate()

        def sendButtonLogic():
            receiver = receiver_input.text().strip()
            amount_text = amount_input.text().strip()
            
            if not receiver:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText("Please enter a valid receiver address.")
                error_popup.exec()
                return
                
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText("Please enter a valid positive amount.")
                error_popup.exec()
                return
                
            # Get selected gas speed
            speed_map = {0: 'slow', 1: 'normal', 2: 'fast'}
            selected_gas_speed = speed_map[gas_speed_combo.currentIndex()]
            
            # Show confirmation dialog with transaction details
            try:
                estimates = eth.getGasFeeEstimates()
                estimate = estimates[selected_gas_speed]
                
                confirmation_text = f"""<html>
<b>Confirm Transaction</b><br><br>
<b>To:</b> {receiver}<br>
<b>Amount:</b> {amount} ETH<br>
<b>Fee:</b> {estimate['fee_eth']:.6f} ETH (${estimate['fee_usd']:.2f})<br>
<b>Total:</b> {amount + estimate['fee_eth']:.6f} ETH<br>
<b>Speed:</b> {gas_speed_combo.currentText()}<br>
<b>Expected time:</b> {estimate['estimated_time']}<br><br>
<i>Do you want to proceed with this transaction?</i>
</html>"""
                
                confirm_popup = QMessageBox()
                confirm_popup.setWindowTitle("Confirm Transaction")
                confirm_popup.setText(confirmation_text)
                confirm_popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                confirm_popup.setDefaultButton(QMessageBox.No)
                
                if confirm_popup.exec() != QMessageBox.Yes:
                    return
                    
            except Exception:
                # Fallback confirmation without detailed estimates
                confirm_popup = QMessageBox()
                confirm_popup.setWindowTitle("Confirm Transaction")
                confirm_popup.setText(f"Send {amount} ETH to {receiver}?")
                confirm_popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                if confirm_popup.exec() != QMessageBox.Yes:
                    return
                
            try:
                TX = eth.createTx(receiver, amount, selected_gas_speed)
                
                # Check if transaction creation failed
                if TX.startswith("Error"):
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Error")
                    error_popup.setText(TX)
                    error_popup.exec()
                    return
                
                ID = eth.broadcastTx(TX)
                
                # Check if broadcast failed
                if ID.startswith("Error"):
                    error_popup = QMessageBox()
                    error_popup.setWindowTitle("Error")
                    error_popup.setText(ID)
                    error_popup.exec()
                    return

                success_popup = QMessageBox()
                success_popup.setWindowTitle("Transaction Sent")
                success_popup.setText(f"Transaction successful. Transaction ID:\n{ID}")
                success_popup.exec()

            except Exception as e:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText(f"Failed to send transaction:\n{str(e)}")
                error_popup.exec()

        send_button = QPushButton("Send Transaction")
        send_button.clicked.connect(sendButtonLogic)
        layout.addWidget(send_button)

    sendEthereum()

    def address():
        ETH_ADDRESS = getEthereumWallet()

        address = QLabel(f"""<html>
Your Ethereum Address Is: {ETH_ADDRESS}
</html>""")
        address.setAlignment(Qt.AlignCenter)
        layout.addWidget(address)

        copy_button = QPushButton("Copy Address To Clipboard")
        def copyButton():
            clipboard = QApplication.clipboard()
            clipboard.setText(ETH_ADDRESS)
        copy_button.clicked.connect(copyButton)
        layout.addWidget(copy_button)
    address()

    def backToMenu():
        back = QPushButton("Back To Menu")
        back.clicked.connect(menuScreen)
        layout.addWidget(back)
    backToMenu()

if __name__ == '__main__':
    startUp()
    sys.exit(app.exec())