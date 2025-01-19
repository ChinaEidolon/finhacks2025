import datetime
from blockchain_logger import BlockchainLogger
from python_encryption import aes_encrypt, aes_decrypt, SimplifiedKyber
from dotenv import load_dotenv
import os
import json
from web3 import Web3


def main():
    # Load environment variables
    load_dotenv()
    web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    print(f"Connected to Ganache: {web3.is_connected()}")
    print(f"Current block number: {web3.eth.block_number}")

    # Define initial amount (can be changed to user input later)
    initial_amount = "100"
    print(f"Initial amount received: {initial_amount}")

    # Encrypt the input
    # Create a Kyber instance to generate a shared secret as the key
    kyber = SimplifiedKyber()
    public_key, private_key = kyber.generate_keypair()  # Generate keypair
    ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
    shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)

    # Use the shared secret as the key for AES encryption
    encrypted_amount = aes_encrypt(initial_amount, shared_secret_receiver)
    print(f"Ciphertext generated: {encrypted_amount}")

    # Create transaction data dictionary
    transaction_data = {
        "encrypted_amount": encrypted_amount,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    # Initialize logger
    logger = BlockchainLogger(
        blockchain_url="http://127.0.0.1:7545",  # Direct URL, no os.getenv needed
        private_key="0x2a52352153b7b7fcc792b913efc9c37656c2ff54f5e9d7008835f2f13a4ddaca",  # Direct private key
        contract_address="0xd52a9d3Bb4441e3640F60f1C431E7A12463EEf48",  # Direct contract address
    )

    # Log transaction
    try:
        tx_hash = logger.log_transaction(
            encrypted_amount=encrypted_amount,
            transaction_data=transaction_data,
            public_amount=0,
        )
        print(f"Transaction hash: {tx_hash}")

        # Verify transaction
        verification = logger.verify_transaction(tx_hash)
        print("\nTransaction verification:")
        print(json.dumps(verification, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    main()
