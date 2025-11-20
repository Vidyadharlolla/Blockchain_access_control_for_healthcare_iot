import json, os, uuid
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from web3 import Web3

# Connect to local blockchain
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected to blockchain:", w3.is_connected())

# Load deployed contract info
with open("../deployed_contract.json") as f:
    deployed = json.load(f)
with open("../contracts/HealthAccessControl_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=deployed["address"], abi=abi)

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def encrypt(text):
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(text).encode())
    return base64.b64encode(cipher.iv + ct).decode(), base64.b64encode(key).decode()

def register_record(bp, hr, spo2):
    device_address = w3.eth.accounts[0]

    data = {"bp": bp, "hr": hr, "spo2": spo2, "time": str(datetime.now())}
    text = json.dumps(data)
    ciphertext, key = encrypt(text)

    rec_id = uuid.uuid4().hex
    pointer_file = f"{rec_id}.txt"

    # Save ciphertext locally
    os.makedirs("../data", exist_ok=True)
    with open(f"../data/{pointer_file}", "w") as f:
        f.write(ciphertext)

    # Convert rec_id to bytes32
    record_id_bytes32 = w3.to_bytes(text=rec_id).ljust(32, b'\0')

    # Register on blockchain
    try:
        tx = contract.functions.registerRecord(record_id_bytes32, device_address, pointer_file).transact({'from': device_address})
        w3.eth.wait_for_transaction_receipt(tx)
        print("\nPatient Data Entered:")
        print(f"Blood Pressure: {bp}")
        print(f"Heart Rate: {hr}")
        print(f"SPO2: {spo2}")
        print(f"\nRecord ID: {rec_id}")
        print(f"Pointer File: {pointer_file}")
        print(f"Encryption Key (keep secret!): {key}")
        print("Record registered on blockchain ✅")
    except Exception as e:
        print("Error registering record:", e)

if __name__ == "__main__":
    bp = input("Enter Blood Pressure (e.g., 120/80): ")
    hr = input("Enter Heart Rate: ")
    spo2 = input("Enter SPO2 %: ")
    register_record(bp, hr, spo2)
