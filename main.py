# Packages
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt
import sys
import os
import json

# Coins
import btc
import eth
import xmr

# Global application and UI components
app = None
window = None
layout = None
config_dir = os.path.expanduser('~/TyWallet')
config_path = os.path.join(config_dir, 'config.json')

def getName():
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["genral"].get("Name", "User")

def getFaveCoin():
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["genral"].get("FaveCoin", "")

def getBitcoinWallet():
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["coins"].get("Bitcoin")

def getMoneroWallet():
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["coins"].get("Monero")

def getEthereumWallet():
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data["coins"].get("Ethereum")


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
    else:
        menuScreen()

    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as config:
            json.dump({
                "coins": {
                    "Bitcoin": False,
                    "Monero": False,
                    "Ethereum": False,
                },
                "genral": {
                    "Name": {},
                    "FavCoin": {},
                }
            }, config, indent=4)
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
                data["genral"]["Name"] = name
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
            menuScreen()

        def faveBitcoin():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["genral"]["FaveCoin"] = "Bitcoin"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        def faveMonero():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["genral"]["FaveCoin"] = "Monero"
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        def faveEthereum():
            with open(config_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data["genral"]["FaveCoin"] = "Ethereum"
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
        title = QLabel(f"""<html>
<b>Hey {NAME}, welcome back to TyWallet!</b><br>
<i>Have you checked up on {FAVE_COIN} yet today?</i>
</html>""")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()

    def cryptoPrice():
        BTC_PRICE = btc.priceGrab()
        ETH_PRICE = eth.priceGrab()
        MONERO_PRICE = xmr.priceGrab()

        price = QLabel(f"""<html>Bitcoin: {BTC_PRICE}<br>
Monero: {MONERO_PRICE}<br>
Ethereum: {ETH_PRICE}<br><br>
<i>Price data from CoinGecko</i>
<html>
""")
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    cryptoPrice()

    def options():

# Use your wallets
        def bitcoinMenu():
            bitcoin = QPushButton("Bitcoin Menu")
            bitcoin.clicked.connect(bitcoinScreen)
            layout.addWidget(bitcoin)
        
        def moneroMenu():
            pass
        
        def ethereumMenu():
            pass

            pass

# Make new wallets
        def makeBitcoinWallet():
            pass

        def makeMoneroWallet():
            pass

        def makeEthereumWallet():
            pass

        if getBitcoinWallet() == False:
            makeBitcoinWallet()
        else:
            bitcoinMenu()

        if getMoneroWallet() == False:
            makeMoneroWallet()
        else:
            moneroMenu()

        if getEthereumWallet == False:
            makeEthereumWallet()
        else:
            ethereumMenu()

    options()

def settings():
    pass

def bitcoinScreen():
    setWindow()

    def title():
        title = QLabel("Bitcoin")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    title()
    
    def price():

        BTC_PRICE = btc.priceGrab()

        price = QLabel(f"""<html>
{BTC_PRICE}
</html>""")
        
        price.setAlignment(Qt.AlignCenter)
        layout.addWidget(price)
    price()

if __name__ == '__main__':
    startUp()
    sys.exit(app.exec())