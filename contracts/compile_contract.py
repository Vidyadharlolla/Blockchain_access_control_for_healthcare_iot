from solcx import compile_standard
import json
import solcx

# Read the Solidity file
with open("HealthAccessControl.sol", "r") as f:
    source = f.read()
solcx.install_solc("0.8.20")
solcx.set_solc_version("0.8.20")

compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"HealthAccessControl.sol": {"content": source}},
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
        }
    }
})

# Extract ABI
abi = compiled_sol['contracts']['HealthAccessControl.sol']['HealthAccessControl']['abi']
with open("HealthAccessControl_abi.json", "w") as f:
    json.dump(abi, f, indent=2)

# Extract Bytecode
bytecode = compiled_sol['contracts']['HealthAccessControl.sol']['HealthAccessControl']['evm']['bytecode']['object']
with open("HealthAccessControl_bytecode.txt", "w") as f:
    f.write(bytecode)

print("Recompiled ABI and bytecode successfully ✅")
