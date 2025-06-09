import os
import json

def getCMC():
    config_dir = os.path.expanduser('~/TyWallet')
    config_path = os.path.join(config_dir, 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["general"].get("CMC_API")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
        return False