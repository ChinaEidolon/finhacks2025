from web3 import Web3
import json
import datetime
from dotenv import load_dotenv


class BlockchainLogger:
    def __init__(self, blockchain_url, private_key, contract_address):
        """
        Initialize the BlockchainLogger with connection details

        Args:
            blockchain_url (str): URL of the blockchain node (e.g. Ethereum)
            private_key (str): Private key for transaction signing
            contract_address (str): Address of the smart contract for logging
        """
        self.web3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.private_key = private_key
        self.contract_address = contract_address

    def log_transaction(self, encrypted_amount, transaction_data=None, public_amount=0):
        """
        Log a transaction with encrypted amount to blockchain
        """
        # Prepare transaction data as bytes
        tx_data = {
            "encrypted_amount": encrypted_amount,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

        if transaction_data:
            tx_data.update(transaction_data)

        # Convert transaction data to JSON string, then to bytes
        data_bytes = json.dumps(tx_data).encode("utf-8")

        # Prepare transaction
        account = self.web3.eth.account.from_key(self.private_key)
        nonce = self.web3.eth.get_transaction_count(account.address)

        # Prepare contract method call
        contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=[
                {
                    "inputs": [
                        {"internalType": "bytes", "name": "data", "type": "bytes"}
                    ],
                    "name": "logTransaction",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function",
                }
            ],
        )

        # Encode the contract method call
        contract_txn = contract.functions.logTransaction(data_bytes).build_transaction(
            {
                "nonce": nonce,
                "gas": 100000,
                "gasPrice": self.web3.eth.gas_price,
                "value": public_amount,
                "chainId": self.web3.eth.chain_id,
            }
        )

        # Sign transaction
        signed_txn = self.web3.eth.account.sign_transaction(
            contract_txn, self.private_key
        )

        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for transaction receipt
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        # Check transaction status
        if tx_receipt["status"] != 1:
            raise ValueError(f"Transaction failed. Receipt: {tx_receipt}")

        return self.web3.to_hex(tx_hash)

    def verify_transaction(self, tx_hash):
        """
        Verify a transaction and get its details

        Args:
            tx_hash (str): Transaction hash to verify

        Returns:
            dict: Transaction details including encrypted amount
        """
        tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
        tx = self.web3.eth.get_transaction(tx_hash)

        # Parse the transaction data from logs
        if tx_receipt["logs"]:
            try:
                # Decode the log data
                log = tx_receipt["logs"][0]
                # Extract the bytes data from the log
                data_bytes = log["data"]
                # Convert bytes to text and parse JSON
                tx_data = json.loads(self.web3.to_text(data_bytes))
            except (json.JSONDecodeError, ValueError) as e:
                tx_data = None

        return {
            "status": tx_receipt["status"],
            "block_number": tx_receipt["blockNumber"],
            "timestamp": datetime.datetime.fromtimestamp(
                self.web3.eth.get_block(tx_receipt["blockNumber"])["timestamp"]
            ).isoformat(),
            "public_value": tx["value"],
            "encrypted_amount": tx_data.get("encrypted_amount") if tx_data else None,
            "additional_data": {
                k: v
                for k, v in (tx_data.items() if tx_data else {}).items()
                if k not in ["encrypted_amount", "timestamp"]
            },
        }
