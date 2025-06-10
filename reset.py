'''
DANGER: Running this will delete all of your local wallets and configurations.
'''

import os
try:
    os.system('rm -rf ~/TyWallet && rm -rf ~/.bitcoinlib')
    print("Local Files Reset Successfully!")

except Exception as e:
    print(f"An error occurred while resetting local files:\n{e}")