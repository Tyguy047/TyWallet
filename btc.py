from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes
import requests
import json

def priceGrab():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd"
        }

        response = requests.get(url, params=params)
        data = response.json()
        price = data["bitcoin"]["usd"]
        return f"${price:,.2f}"
    
    except Exception:
        return "Error: Price data could not be fetched!"

def balanceCkeck():
    try:
        pass

    except Exception:
        return "An error occured when fetching your balance! Don't worry your funds are most likley okay this is probably an error on our end retreiving your balance!"

def walletGen():

    def seed():
        pass

    def privateKey():
        pass

    def publicKey():
        pass

    # 1. Generate a 24-word mnemonic
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(24)
    print("Mnemonic:", mnemonic)

    # 2. Generate the seed from the mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # 3. Generate the BIP84 wallet (for Bitcoin native SegWit: bc1 addresses)
    bip84_wallet = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)

    # 4. Get the first account
    account = bip84_wallet.Purpose().Coin().Account(0)

    # 5. External chain (receiving addresses)
    change = account.Change(Bip44Changes.CHAIN_EXT)

    # 6. Get the first address (index 0)
    address = change.AddressIndex(0).PublicKey().ToAddress()

    print("Bitcoin Address:", address)
    print("Public Key:", change.AddressIndex(0).PublicKey().RawCompressed().ToHex())
    print("Private Key (WIF):", change.AddressIndex(0).PrivateKey().ToWif())