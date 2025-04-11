import subprocess
import re
import os
from dotenv import load_dotenv
import time


def deploy_contract():
    print(
        "IMPORTANT: Make sure you have started Hardhat node in a separate terminal with:"
    )
    print("  npx hardhat node")

    print("\nDeploying contract to local Hardhat network...")
    # Deploy the contract assuming the Hardhat node is running in a separate shell
    result = subprocess.run(
        ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "localhost"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error deploying contract:\n{result.stderr}")
        print("\nMake sure you have started the Hardhat node in a separate terminal.")
        return None

    print(f"Deployment output:\n{result.stdout}")

    address_match = re.search(r"0x[a-fA-F0-9]{40}", result.stdout)
    if not address_match:
        print("Could not find contract address in deployment output")
        return None

    contract_address = address_match.group(0)
    print(f"Contract deployed at: {contract_address}")
    return contract_address


def update_env_file(contract_address):
    if not contract_address:
        return False

    load_dotenv()
    env_path = "../.env"
    if not os.path.exists(env_path):
        print("Create a new .env file copying .env.example ")
        raise FileNotFoundError(f"{env_path} not found")

    with open(env_path, "r") as f:
        lines = f.readlines()

    found = False
    new_lines = []
    for line in lines:
        if line.startswith("CONTRACT_ADDRESS="):
            new_lines.append(f"CONTRACT_ADDRESS={contract_address}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"CONTRACT_ADDRESS={contract_address}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print(f"Updated .env file with CONTRACT_ADDRESS={contract_address}")
    return True


if __name__ == "__main__":
    contract_address = deploy_contract()
    if contract_address:
        if update_env_file(contract_address):
            print("Setup complete! You can now run your application.")
        else:
            print("Failed to update .env file.")
    else:
        print("Contract deployment failed.")
