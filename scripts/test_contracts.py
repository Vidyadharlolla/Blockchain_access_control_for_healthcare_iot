import json
import random
from web3 import Web3

# Connect to local blockchain
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected:", w3.is_connected())

# Load deployed contract JSON (correct file path!)
with open(r"C:\Users\JAYA\OneDrive\Desktop\crypto\deployed_contract.json", "r") as f:
    deployed = json.load(f)

contract_address = deployed["address"]
abi = deployed["abi"]  # Make sure your deployed_contract.json contains the ABI

health = w3.eth.contract(address=contract_address, abi=abi)

# Accounts
admin = w3.eth.accounts[0]
doctor = w3.eth.accounts[1]
attacker = w3.eth.accounts[2]

print("Admin:", admin)
print("Doctor:", doctor)
print("Attacker:", attacker)

# Helper: generate random record ID
def generate_record_id():
    return w3.keccak(text=str(random.randint(1, 1_000_000)))

# Register a record
def register_record(record_id, owner, pointer):
    tx = health.functions.registerRecord(record_id, owner, pointer).transact({'from': admin})
    w3.eth.wait_for_transaction_receipt(tx)
    print("Record registered ✅")

# Grant access
def grant_access(record_id, grantee, expires_at=0):
    tx = health.functions.grantAccess(record_id, grantee, expires_at).transact({'from': admin})
    w3.eth.wait_for_transaction_receipt(tx)
    print("Access granted to doctor ✅")

# Revoke access (set expiresAt=1 to simulate revocation)
def revoke_access(record_id, grantee):
    tx = health.functions.grantAccess(record_id, grantee, 1).transact({'from': admin})
    w3.eth.wait_for_transaction_receipt(tx)
    print("Doctor access revoked ✅")

# Request access (detect authorized / unauthorized)
def request_access(record_id, requester, role_name):
    tx = health.functions.requestAccess(record_id).transact({'from': requester})
    receipt = w3.eth.wait_for_transaction_receipt(tx)

    authorized = False
    for log in receipt.logs:
        try:
            event = health.events.AccessGranted().processLog(log)
            authorized = True
            break
        except:
            try:
                event = health.events.UnauthorizedAccessAttempt().processLog(log)
                authorized = False
                break
            except:
                continue

    if authorized:
        print(f"{role_name} access confirmed ✅")
    else:
        print(f"Unauthorized access detected ✅")

# --- Run test cases ---
print("\n--- Running Test Cases ---")

record_id = generate_record_id()

# 1. Register record
register_record(record_id, admin, "ipfs://dummyPointer")

# 2. Grant access to doctor
grant_access(record_id, doctor)

# 3. Doctor requests access
request_access(record_id, doctor, "Doctor")

# 4. Attacker tries unauthorized access
request_access(record_id, attacker, "Attacker")

# 5. Revoke doctor access
revoke_access(record_id, doctor)

# 6. Doctor tries access after revocation
request_access(record_id, doctor, "Doctor")

print("\n✅ All test cases executed successfully!")


