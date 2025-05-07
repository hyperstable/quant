from typing import Literal, TypedDict, Union

import requests
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

from dotenv import load_dotenv
import os

load_dotenv()

# Define API URL directly since we can't import constants
main_net = False
API_URL = (
    "https://api.hyperliquid.xyz"
    if main_net is True
    else "https://api.hyperliquid-testnet.xyz"
)

from hyperliquid.utils.signing import get_timestamp_ms, sign_l1_action


wei_decimals_core = 5
wei_decimals_extra = 18 - wei_decimals_core

DEFAULT_CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x0a200360D5f614Aa7C7842fBA9C244B27c8904E4"  # change this to your contract address if you are skipping deploying
)
MNEMONIC = (
    "<YOUR MNEMONIC>"  # Change this to your menomic if you want to use a mnemonic
)
USE_MENOMIC = False
PRIVATE_KEY = os.getenv("PK")  # Change this to your private key otherwise

# Connect to the JSON-RPC endpoint
rpc_url = (
    "https://rpc.hyperliquid.xyz/evm"
    if main_net is True
    else "https://rpc.hyperliquid-testnet.xyz/evm"
)
w3 = Web3(Web3.HTTPProvider(rpc_url))

# The account will be used both for deploying the ERC20 contract and linking it to your native spot asset
# You can also switch this to create an account a different way if you don't want to include a secret key in code
if USE_MENOMIC:
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(MNEMONIC)
    print(f"Running with address {account.address}")
    w3.middleware_onion.add(SignAndSendRawMiddlewareBuilder.build(account))
    w3.eth.default_account = account.address
else:
    account: LocalAccount = Account.from_key(PRIVATE_KEY)
    print(f"Running with address {account.address}")
    w3.middleware_onion.add(SignAndSendRawMiddlewareBuilder.build(account))
    w3.eth.default_account = account.address
# Verify connection
if not w3.is_connected():
    raise Exception("Failed to connect to the Ethereum network")


creation_nonce: int
contract_address = DEFAULT_CONTRACT_ADDRESS

# token creation nonce
creation_nonce = 446


TOKEN = 1304  # Token Index in the UI
system_user_extension = f"{TOKEN:x}"

system_address = "0x2" + "0" * (39 - len(system_user_extension)) + system_user_extension

TOTAL_SUPPLY = 10_000_000_000
amount_wei = TOTAL_SUPPLY * (10**wei_decimals_core)  # 100B with 6 wei decimals

# step 1: done
user_genesis_action = {
    "type": "spotDeploy",
    "userGenesis": {
        "token": TOKEN,
        "userAndWei": [[system_address, str(amount_wei)]],
        "existingTokenAndWei": [],
    },
}

# step 2: done
genesis_action = {
    "type": "spotDeploy",
    "genesis": {"token": TOKEN, "maxSupply": str(amount_wei), "noHyperliquidity": True},
}

# step 3: done
# safe spot id and adjust in code
# Response status code: 200
# Raw response content: {"status":"ok","response":{"type":"spot","data":1181}}
# UserGenesis response: {'status': 'ok', 'response': {'type': 'spot', 'data': 1181}}
# here we wat 1181
SPOT = 1181  # comes from register spot action
register_spot = {"type": "spotDeploy", "registerSpot": {"tokens": [TOKEN, 0]}}

# step 4: done
# no hyperliquidity since our supply is on HyperEVM
# there won't be any hyperliquidity orders
# here set to $1 -> we want to deploy this with the actual PEG price $0.04
# "startPx": "1" -> "startPx": "0.04"
hyper_liquidity_action = {
    "type": "spotDeploy",
    "registerHyperliquidity": {
        "spot": SPOT,
        "startPx": "1",
        "orderSz": "0",
        "nOrders": 0,
    },
}

# step 5: done
request_evm_contract = {
    "type": "spotDeploy",
    "requestEvmContract": {
        "token": TOKEN,
        "address": contract_address.lower(),
        "evmExtraWeiDecimals": wei_decimals_extra,
    },
}

# step 6: done
finalize_action = {
    "type": "finalizeEvmContract",
    "token": TOKEN,
    "input": {"create": {"nonce": creation_nonce}},
}

nonce = get_timestamp_ms()

# change action according to step
action = finalize_action

signature = sign_l1_action(account, action, None, nonce, None, main_net)

payload = {
    "action": action,
    "nonce": nonce,
    "signature": signature,
    "vaultAddress": None,
}


print(payload)
response = requests.post(API_URL + "/exchange", json=payload, timeout=10)
print("Response status code:", response.status_code)
print("Raw response content:", response.text)
try:
    print("UserGenesis response:", response.text)
except requests.exceptions.JSONDecodeError as e:
    print("Failed to parse JSON response:", e)
