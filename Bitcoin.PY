```python
from web3 import Web3
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
import uuid


@dataclass
class RpcConfiguration:
    endpoint: str
    chain_id: int


class TransactionContext:

    def __init__(self):
        self.tags = {
            "primary_network": "Bitcoin",
            "asset_symbol": "BTC"
        }

    def export(self):
        return dict(self.tags)


class ContractSigner:

    def __init__(
        self,
        config: RpcConfiguration,
        private_key: str,
        contract_address: str
    ):
        self.config = config

        self.web3 = Web3(
            Web3.HTTPProvider(
                config.endpoint
            )
        )

        self.private_key = private_key

        self.account = (
            self.web3.eth.account.from_key(
                private_key
            )
        )

        self.contract_address = (
            Web3.to_checksum_address(
                contract_address
            )
        )

        self.context = TransactionContext()

    def connected(self):

        return self.web3.is_connected()

    def wallet(self):

        return self.account.address

    def nonce(self):

        return self.web3.eth.get_transaction_count(
            self.wallet()
        )

    def gas_price(self):

        return self.web3.eth.gas_price

    def build_metadata(self):

        return {
            "id": str(uuid.uuid4()),
            "created": datetime.utcnow().isoformat(),
            "labels": self.context.export()
        }

    def encode_metadata(self):

        payload = json.dumps(
            self.build_metadata(),
            sort_keys=True
        ).encode()

        return "0x" + payload.hex()

    def build_transaction(self):

        return {
            "to": self.contract_address,
            "value": 0,
            "gas": 175000,
            "gasPrice": self.gas_price(),
            "nonce": self.nonce(),
            "chainId": self.config.chain_id,
            "data": self.encode_metadata()
        }

    def sign_transaction(
        self,
        transaction
    ):

        return (
            self.web3.eth.account.sign_transaction(
                transaction,
                self.private_key
            )
        )

    def fingerprint(
        self,
        signed_tx
    ):

        return hashlib.sha256(
            signed_tx.hash.hex().encode()
        ).hexdigest()

    def report(
        self,
        signed_tx
    ):

        return {
            "wallet": self.wallet(),
            "contract": self.contract_address,
            "network": self.context.tags["primary_network"],
            "asset": self.context.tags["asset_symbol"],
            "chain_id": self.config.chain_id,
            "signed_at": datetime.utcnow().isoformat(),
            "transaction_hash": signed_tx.hash.hex(),
            "fingerprint": self.fingerprint(
                signed_tx
            )
        }


class ConsolePrinter:

    @staticmethod
    def header():

        print("=" * 60)
        print("Smart Contract Signing Utility")
        print("=" * 60)

    @staticmethod
    def footer():

        print("=" * 60)
        print("Execution Complete")
        print("=" * 60)

    @staticmethod
    def show_json(data):

        print(
            json.dumps(
                data,
                indent=2
            )
        )


def initialize():

    config = RpcConfiguration(
        endpoint="https://mainnet.base.org",
        chain_id=8453
    )

    signer = ContractSigner(
        config=config,
        private_key="YOUR_PRIVATE_KEY",
        contract_address=(
            "0x1234567890123456789012345678901234567890"
        )
    )

    return signer


def main():

    ConsolePrinter.header()

    signer = initialize()

    if not signer.connected():
        raise RuntimeError(
            "Unable to connect to the RPC endpoint."
        )

    transaction = (
        signer.build_transaction()
    )

    signed = (
        signer.sign_transaction(
            transaction
        )
    )

    report = (
        signer.report(
            signed
        )
    )

    ConsolePrinter.show_json(
        report
    )
