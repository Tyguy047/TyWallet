# Packages
from PySide6.QtWidgets import QMessageBox, QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, QObject, Signal
import sys
import os
import json
from cryptography.fernet import Fernet
from utils import getCMC

# Coins
import btc
import eth
import xmr

class PriceUpdater(QObject):
    price_signal = Signal(str, str)
# Global application and UI components
app = None
window = None
layout = None
config_dir = os.path.expanduser('~/TyWallet')
config_path = os.path.join(config_dir, 'config.json')
key_path = os.path.join(config_dir, 'wallet.key')



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

def readKey():
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
    return key

def encryptData(key, data):
    fernet = Fernet(key)
    if isinstance(data, str):
        data = data.encode()
    encrypted = fernet.encrypt(data)
    return encrypted.decode()


# Decrypts data using Fernet key
def decryptData(key, encrypted_data):
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()

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
    
    if not os.path.exists(key_path):
        with open(key_path, 'wb') as key_file:  # binary write mode
            key = Fernet.generate_key()
            key_file.write(key)

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as config:
            json.dump({
                "coins": {
                    "Bitcoin": False,
                    "Monero": False,
                    "Ethereum": False,
                },
                "privkeys": {
                    "Bitcoin": {},
                    "Monero": {},
                    "Ethereum": {},
                },
                "pubkeys": {
                    "Bitcoin": {},
                    "Monero": {},
                    "Ethereum": {},
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

    def setCMC():

        def saveAPI():
            api_key = inputAPI.text()
            with open(config_path, 'r+', encoding='utf-8') as config:
                data = json.load(config)
                data["general"]["CMC_API"] = api_key
                config.seek(0)
                json.dump(data, config, indent=4)
                config.truncate()
            menuScreen()

        inputAPItext = QLabel("Enter your CoinMarketCap API Key:")
        inputAPItext.setAlignment(Qt.AlignCenter)
        layout.addWidget(inputAPItext)

        inputAPI = QLineEdit()
        inputAPI.setAlignment(Qt.AlignCenter)
        layout.addWidget(inputAPI)

        submit_btn = QPushButton("Save API Key")
        submit_btn.clicked.connect(saveAPI)
        layout.addWidget(submit_btn, alignment=Qt.AlignCenter)


    if getCMC() == False:
        setCMC()

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
        BTC_PRICE = "Loading..."
        ETH_PRICE = "Loading..."
        MONERO_PRICE = "Loading..."

        price = QLabel(f"""<html>Bitcoin: {BTC_PRICE}<br>
    Monero: {MONERO_PRICE}<br>
    Ethereum: {ETH_PRICE}<br><br>
    <i>Price data from CoinMarketCap</i>
    <html>
    """)
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)

        updater = PriceUpdater()
        latest = {"btc": BTC_PRICE, "eth": ETH_PRICE, "xmr": MONERO_PRICE}

        def update_label():
            # Show exactly what is returned for each coin, including error messages
            price.setText(f"""<html>Bitcoin: {latest['btc']}<br>
    Monero: {latest['xmr']}<br>
    Ethereum: {latest['eth']}<br><br>
    <i>Price data from CoinMarketCap</i>
    <html>""")

        def on_price_update(coin, value):
            print(f"Updated price for {coin}: {value}")
            latest[coin] = value  # Store the exact returned value, including error messages
            update_label()

        updater.price_signal.connect(on_price_update)

        def fetch_btc():
            try:
                btc_val = btc.priceGrab()
            except Exception as e:
                btc_val = "Error"
            updater.price_signal.emit('btc', btc_val)

        def fetch_eth():
            try:
                eth_val = eth.priceGrab()
            except Exception as e:
                eth_val = "Error"
            updater.price_signal.emit('eth', eth_val)

        def fetch_xmr():
            try:
                xmr_val = xmr.priceGrab()
            except Exception as e:
                xmr_val = "Error"
            updater.price_signal.emit('xmr', xmr_val)

        def fetch_all_prices():
            fetch_btc()
            fetch_eth()
            fetch_xmr()
        fetch_all_prices()
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

                ENCRYPTION_KEY_FILE = readKey()

                WALLET_GEN = btc.walletGen()
                SEED = WALLET_GEN["mnemonic"]
                ADDRESS = WALLET_GEN["address"]
                PRIVATE_KEY = WALLET_GEN["private_key"]
                PUBLIC_KEY = WALLET_GEN["public_key"]
                with open(config_path, 'r+', encoding='utf-8') as config:
                    data = json.load(config)
                    data["coins"]["Bitcoin"] = True

                    ENC_PRIV_KEY = encryptData(ENCRYPTION_KEY_FILE, PRIVATE_KEY)

                    data["privkeys"]["Bitcoin"] = ENC_PRIV_KEY
                    data["pubkeys"]["Bitcoin"] = PUBLIC_KEY
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

        # Remove empty placeholder functions for makeMoneroWallet and makeEthereumWallet

        if not checkBitcoinWallet():
            makeBitcoinWallet()
        else:
            bitcoinMenu()
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
<i>Pending funds are still processing and are not able to be spent yet!</i>
</html>""")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    balance()

    def price():
        BTC_PRICE = btc.priceGrab()

        price = QLabel(f"""<html>
{BTC_PRICE}
</html>""")
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    price()

    def sendBitcoin():

        ENCRYPTION_KEY_FILE = readKey()
        with open(config_path, 'r', encoding='utf-8') as config:
            data = json.load(config)
            encrypted_priv_key = data["privkeys"]["Bitcoin"]
            PRIVATE_KEY = decryptData(ENCRYPTION_KEY_FILE, encrypted_priv_key)

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
        send_button.clicked.connect(lambda: btc.sendBTC(receiver_input.text(), amount_input.text(), PRIVATE_KEY))
        layout.addWidget(send_button)
    sendBitcoin()

    def address():
        BTC_ADDRESS = getBitcoinWallet()

        address = QLabel(f"""<html>
Your Bitcoin Address Is: {BTC_ADDRESS}
</html>""")
        address.setAlignment(Qt.AlignCenter)
        layout.addWidget(address)
    address()

    def backToMenu():
        back = QPushButton("Back To Menu")
        back.clicked.connect(menuScreen)
        layout.addWidget(back)
    backToMenu()

if __name__ == '__main__':
    startUp()
    sys.exit(app.exec())