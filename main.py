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
            return data["coins"].get("Ethereum")
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
            pass

        def makeMoneroWallet():
            pass

        def ethereumMenu():
            ethereum = QPushButton("Ethereum Menu")
            ethereum.clicked.connect(ethereumScreen)
            layout.addWidget(ethereum)

        def makeEthereumWallet():
            WALLET = eth.walletGen()

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
        BTC_BALANCE = btc.balanceCheck()
        CONFIRMED = BTC_BALANCE["confirmed_balance"]
        PENDING = BTC_BALANCE["unconfirmed_balance"]

        title = QLabel(f"""<html>
Your current confirmed balance is: {CONFIRMED}.<br><br>
Your current pending balance is: {PENDING}.<br><br><br>
<i>Pending funds are still processing and are not able to be spent yet!<br>
If your unconfirmed balance is negative it means that you have an out going transaction.</i>
</html>""")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    try:
        balance()
    except Exception:
        pass

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
                success_popup = QMessageBox()
                success_popup.setWindowTitle("Transaction Sent")
                success_popup.setText(f"Transaction successful. Transaction ID:\n{tx_result}")
                success_popup.exec()
            except Exception as e:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText(f"Failed to send transaction:\n{str(e)}")
                error_popup.exec()

        send_button.clicked.connect(on_send_click)
        layout.addWidget(send_button)
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
        ETH_BALANCE = eth.balanceCheck()

        balance = QLabel(f"""<html>
Your current confirmed balance is: {ETH_BALANCE} ETH.<br><br><br>
</html>""")
        balance.setAlignment(Qt.AlignCenter)
        layout.addWidget(balance)
    balance()

    def sendEthereum():
        pass
        receiver_label = QLabel("Enter the Ethereum address of who will be receiving the fund you wish to send")
        receiver_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_label)

        receiver_input = QLineEdit()
        receiver_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(receiver_input)


        amount_label = QLabel("Enter the amount of ETH you would like to send")
        amount_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_label)

        amount_input = QLineEdit()
        amount_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(amount_input)

        def sendButtonLogic():
            try:
                TX = eth.createTx(receiver_input.text(), amount_input.text())
                ID = eth.broadcastTx(TX)

                success_popup = QMessageBox()
                success_popup.setWindowTitle("Transaction Sent")
                success_popup.setText(f"Transaction successful. Transaction ID:\n{ID}")
                success_popup.exec()

            except Exception:
                error_popup = QMessageBox()
                error_popup.setWindowTitle("Error")
                error_popup.setText(f"An error occurred while sending the transaction!")
                error_popup.exec()



        send_button = QPushButton("Send Transaction")
        send_button.setAlignment(Qt.AlignCenter)
        send_button.clicked.connect(sendButtonLogic)
        layout.addWidget(send_button)


    sendEthereum()

if __name__ == '__main__':
    startUp()
    sys.exit(app.exec())