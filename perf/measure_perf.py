import json, time
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
with open("../deployed_contract.json") as f:
    deployed = json.load(f)

contract = w3.eth.contract(address=deployed['address'], abi=deployed['abi'])
patient = w3.eth.accounts[1]
doctor = w3.eth.accounts[2]

record_id = w3.keccak(text="demo-record")
start = time.time()
tx = contract.functions.registerRecord(record_id, patient, "demo.txt").transact({'from': patient})
receipt = w3.eth.wait_for_transaction_receipt(tx)
end = time.time()

print("Gas used:", receipt.gasUsed)
print("Latency:", end - start, "seconds")
