from web3 import Web3
import json
import os

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected:", w3.is_connected())

deployer = w3.eth.accounts[0]
print("Deployer account:", deployer)

# Load ABI & Bytecode (from contracts folder)
base_path = "../contracts"
abi_path = os.path.join(base_path, "HealthAccessControl_abi.json")
bytecode_path = os.path.join(base_path, "HealthAccessControl_bytecode.txt")

# Read ABI
with open(abi_path) as f:
    abi = json.load(f)

# Read bytecode
with open(bytecode_path) as f:
    bytecode = f.read().strip()

print("Bytecode preview:", bytecode[:20])

# Deploy the contract
print("Deploying contract...")
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = contract.constructor().transact({"from": deployer})
print("Transaction hash:", tx_hash.hex())

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt["contractAddress"]
print("✅ Contract deployed successfully!")
print("Contract address:", contract_address)

# SAVE deployed contract details
output_path = "../deployed_contract.json"   # <-- FIXED PATH

with open(output_path, "w") as f:
    json.dump({"address": contract_address, "abi": abi}, f, indent=4)

print("Saved deployment details to:", output_path)


