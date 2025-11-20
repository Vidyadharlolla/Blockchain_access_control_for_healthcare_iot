import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print("Connected:", w3.is_connected())

with open("../deployed_contract.json") as f:
    deployed = json.load(f)
with open("../contracts/HealthAccessControl_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=deployed["address"], abi=abi)

def check_access():
    rec_id = input("Enter Record ID (without .txt): ").strip()
    doctor = w3.eth.accounts[1]

    record_id_bytes32 = w3.to_bytes(text=rec_id).ljust(32, b'\0')

    # Get AccessGranted events
    granted_events = contract.events.AccessGranted.get_logs(from_block=0, to_block='latest')
    granted = any(e['args']['recordId'] == record_id_bytes32 and e['args']['requester'] == doctor for e in granted_events)

    if granted:
        print(f"✅ Blockchain approved access for record {rec_id} to doctor {doctor}")
    else:
        print(f"❌ No access granted for record {rec_id} to doctor {doctor}")

if __name__ == "__main__":
    check_access()
