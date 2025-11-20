import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected:", w3.is_connected())

with open("../deployed_contract.json") as f:
    deployed = json.load(f)
with open("../contracts/HealthAccessControl_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=deployed["address"], abi=abi)
patient_account = w3.eth.accounts[0]

def grant_access():
    rec_id = input("Enter Record ID to grant access (without .txt): ").strip()
    expiry = int(input("Enter expiry timestamp (0 for no expiry): ").strip())

    # For demo, grant access to doctor (account 1)
    doctor_address = w3.eth.accounts[1]

    # Convert rec_id to bytes32
    record_id_bytes32 = w3.to_bytes(text=rec_id).ljust(32, b'\0')

    # Grant access
    try:
        tx = contract.functions.grantAccess(record_id_bytes32, doctor_address, expiry).transact({'from': patient_account})
        w3.eth.wait_for_transaction_receipt(tx)
        print("✅ Access granted successfully!")
    except Exception as e:
        if "no record" in str(e):
            print("❌ Record does not exist on blockchain. Please register it first.")
        else:
            print("Error granting access:", e)

if __name__ == "__main__":
    grant_access()
