# 🔐 TyWallet

[![Python 3.13.4](https://img.shields.io/badge/python-3.13.4-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open Source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/)

**The Open Source Cryptocurrency Wallet Built for Everyone**

TyWallet is a free, secure, and beginner-friendly cryptocurrency wallet built with Python. It supports Bitcoin, Ethereum, and Monero with a focus on simplicity, security, and customization.

## ✨ Why TyWallet?

- **🔒 Security First**: Your private keys never leave your device
- **🐍 Python-Powered**: Easy to understand, modify, and extend
- **🌟 Beginner Friendly**: Simple interface designed for crypto newcomers
- **⚡ Real-time Prices**: Live cryptocurrency prices via our free API
- **🔧 Fully Customizable**: Open source - modify anything you want
- **🆓 Completely Free**: No fees, no premium features, forever

## 🚀 Features

### Wallet Management
- **Multi-Cryptocurrency Support**: Bitcoin (BTC), Ethereum (ETH), and Monero (XMR)
- **Secure Wallet Generation**: Industry-standard cryptographic security
- **Local Storage**: All data encrypted and stored locally on your device
- **Import/Export**: Easy wallet backup and recovery with seed phrases

### Trading & Transactions
- **Send Cryptocurrency**: Simple interface for sending transactions
- **Balance Checking**: Real-time balance updates
- **Smart Fee Calculation**: Automatic optimal fee calculation
- **Testnet Support**: Safe development and testing environment

### Price Tracking
- **Live Price API**: Real-time cryptocurrency prices
- **Free Forever**: No rate limits or API keys required
- **Privacy-Focused**: .onion Tor endpoints available

## 📦 Installation

### Prerequisites
- Python 3.13.4 or higher
- pip (Python package installer)
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Tyguy047/TyWallet.git
   cd TyWallet
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch TyWallet**
   ```bash
   python main.py
   ```

That's it! TyWallet will create its configuration directory at `~/TyWallet` on first run.

## 🌐 Free Cryptocurrency API

TyWallet includes a completely free, unlimited cryptocurrency price API that anyone can use.

### API Endpoints

**Base URL**: `https://api.tywallet.xyz`

- **Bitcoin**: `GET /prices/bitcoin`
- **Ethereum**: `GET /prices/ethereum`
- **Monero**: `GET /prices/monero`

**Privacy-Focused Tor Endpoint**: `http://cbckdpjeksawellm4z2ttub3vmn552hnaagrsjueugfs4bzk5lzcyqqd.onion`

### Example Usage

```python
import requests

# Get Bitcoin price
response = requests.get('https://api.tywallet.xyz/prices/bitcoin')
btc_price = response.text
print(f"Bitcoin: ${btc_price}")
```

```bash
# Using cURL
curl https://api.tywallet.xyz/prices/bitcoin
```

### API Features
- ✅ No authentication required
- ✅ No rate limiting
- ✅ CORS enabled for web applications
- ✅ Privacy-focused Tor endpoints

## 🛠️ Development

### Project Structure
```
TyWallet/
├── main.py                 # Main GUI application
├── btc.py                  # Bitcoin wallet operations
├── eth.py                  # Ethereum wallet operations
├── xmr.py                  # Monero wallet operations
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── reset.py               # Wallet reset utility
├── CoinValueBackend/      # API server code
│   ├── server.py          # Flask API server
│   └── backend_requirements.txt
└── assets/               # UI assets and icons
    └── coin_icons/       # Cryptocurrency icons
```

### Key Dependencies
- **PySide6**: Cross-platform GUI framework
- **requests**: HTTP library for API calls
- **bip_utils**: Bitcoin address generation utilities
- **web3**: Ethereum blockchain interaction
- **cryptography**: Encryption and security functions
- **bitcoinlib**: Bitcoin wallet operations
- **eth-account**: Ethereum account management

### Configuration
TyWallet stores its configuration in `~/TyWallet/config.json`:

```json
{
    "coins": {
        "Bitcoin": false,
        "Monero": false,
        "Ethereum": false
    },
    "addresses": {
        "Bitcoin": {},
        "Monero": {},
        "Ethereum": {}
    },
    "general": {
        "Name": "User",
        "FaveCoin": "Bitcoin",
        "CMC_API": false
    }
}
```

## 🔧 Customization

TyWallet is designed to be easily customizable:

### Adding New Cryptocurrencies

1. Create a new module (e.g., `ltc.py` for Litecoin)
2. Implement required functions:
   ```python
   def walletGen():
       """Generate new wallet"""
       pass
   
   def balanceCheck():
       """Check wallet balance"""
       pass
   
   def priceGrab():
       """Get current price"""
       pass
   ```
3. Update `main.py` to include the new cryptocurrency
4. Add to configuration structure

### Modifying the GUI
The interface is built with PySide6 (Qt). You can easily modify:
- Window layouts
- Button styles
- Color schemes
- Add new features

## 🔒 Security

### Security Features
- **Local Storage**: All wallet data stored locally, never on servers
- **Encryption**: Industry-standard encryption for all sensitive data
- **Private Key Security**: Private keys never transmitted over networks
- **Open Source**: Code can be audited by anyone
- **Testnet Support**: Safe testing environment

### Best Practices
- 🔐 Never share your private keys or seed phrases
- 📝 Write down seed phrases and store them securely offline
- 💾 Regularly backup your wallet files
- 🔄 Keep TyWallet updated to the latest version
- 🛡️ Use reliable antivirus software

## 📚 Documentation

For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md) which includes:
- Complete installation guide
- API documentation
- Development setup
- Security guidelines
- Troubleshooting
- Contributing guidelines

## 🌐 Links

- **Website**: [www.tywallet.xyz](https://www.tywallet.xyz)
- **Free API**: [api.tywallet.xyz](https://api.tywallet.xyz)
- **Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/Tyguy047/TyWallet/issues)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Report Bugs**: Open an issue on GitHub
- ✨ **Suggest Features**: Share your ideas for improvements
- 🔧 **Submit Code**: Create pull requests for bug fixes or features
- 📚 **Improve Documentation**: Help make our docs better
- 🌍 **Translate**: Help translate TyWallet to other languages

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📋 System Requirements

- **Operating System**: MacOS, or Linux
- **Python**: 3.13.4 or higher
- **Network**: Internet connection for price updates and transactions

## 🚨 Troubleshooting

### Common Issues

**Installation fails with dependency errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**GUI doesn't start:**
```bash
pip uninstall PySide6
pip install PySide6
```

**Reset wallet (⚠️ DANGER - deletes all wallets):**
```bash
python reset.py
```

For more troubleshooting help, see [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting).

## 📄 License

TyWallet is open source software released under the [MIT License](LICENSE).

## 🎯 Roadmap


### Long-term Goals
- 🎨 Customizable themes

## 💖 Support TyWallet

If you find TyWallet useful, please consider:

- ⭐ Starring this repository
- 🗣️ Telling others about TyWallet
- 💰 Making a donation:
  - **Bitcoin**: `[Bitcoin Address]`
  - **Ethereum**: `[Ethereum Address]`
  - **Monero**: `[Monero Address]`

## 📞 Contact

- **Email**: getintouch@tylercaselli.com
- **Website**: [www.tywallet.xyz](https://www.tywallet.xyz)
- **Issues**: [GitHub Issues](https://github.com/Tyguy047/TyWallet/issues)

---

<div align="center">
  <strong>Made with ❤️ for the cryptocurrency community</strong>
  <br>
  <sub>TyWallet - Secure, Simple, Free</sub>
</div>
