from blockchain_logger import BlockchainLogger
from dotenv import load_dotenv
import os
import json


def main():
    # Load environment variables
    load_dotenv()

    # Initialize logger
    logger = BlockchainLogger(
        blockchain_url="http://127.0.0.1:7545",  # Direct URL, no os.getenv needed
        private_key="79d0d15ac57ecb8ceb9abc1807b04376a5b4972ee944443a9fcfa009ce14b3c4",  # Direct private key
        contract_address="0x6f769A0340e23EE54B43546EE57b14aa0f3cEC8F",  # Direct contract address
    )

    # Example encrypted amount
    encrypted_amount = "jH3gcAsn7yNI+3EkTq9cQPo/lXVv2LgHIEZ2ZUsE1gk"

    # Log transaction
    try:
        tx_hash = logger.log_transaction(
            encrypted_amount=encrypted_amount, public_amount=0
        )
        print(f"Transaction hash: {tx_hash}")

        # Verify transaction
        verification = logger.verify_transaction(tx_hash)
        print("\nTransaction verification:")
        print(json.dumps(verification, indent=2))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
