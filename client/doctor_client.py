import json, base64
from Crypto.Cipher import AES
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected:", w3.is_connected())

with open("../deployed_contract.json") as f:
    deployed = json.load(f)
with open("../contracts/HealthAccessControl_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=deployed["address"], abi=abi)
doctor_account = w3.eth.accounts[1]

def decrypt_record(ciphertext, key):
    raw = base64.b64decode(ciphertext)
    key_bytes = base64.b64decode(key)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    # Remove padding
    pad_len = pt[-1]
    return pt[:-pad_len].decode()

def request_access():
    rec_id = input("Enter Record ID (without .txt): ").strip()

    # Convert rec_id to bytes32
    record_id_bytes32 = w3.to_bytes(text=rec_id).ljust(32, b'\0')

    # Request access
    try:
        tx = contract.functions.requestAccess(record_id_bytes32).transact({'from': doctor_account})
        w3.eth.wait_for_transaction_receipt(tx)

        # Check if access granted
        events = contract.events.AccessGranted.get_logs(from_block=0, to_block='latest')
        granted = any(e['args']['recordId'] == record_id_bytes32 and e['args']['requester'] == doctor_account for e in events)

        if granted:
            print("✅ Access request approved by blockchain!")
            key = input("Enter AES Key provided by patient: ").strip()

            # Load ciphertext
            with open(f"../data/{rec_id}.txt") as f:
                ciphertext = f.read()
            decrypted = decrypt_record(ciphertext, key)
            print("Decrypted patient record:\n", decrypted)
        else:
            print("❌ Access request denied by blockchain.")

    except Exception as e:
        print("Error requesting access:", e)

if __name__ == "__main__":
    request_access()
