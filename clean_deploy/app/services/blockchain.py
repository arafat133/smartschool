import hashlib
import json
from typing import Dict, Any

class BlockchainSimulator:
    @staticmethod
    def generate_hash(data: Dict[str, Any], previous_hash: str = "0") -> str:
        """
        Generate SHA-256 hash for a given dataset and the previous hash.
        This simulates the immutability of blockchain.
        """
        block = {
            "data": data,
            "previous_hash": previous_hash
        }
        # Ensure the dictionary is ordered to produce consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def verify_integrity(data: Dict[str, Any], previous_hash: str, current_hash: str) -> bool:
        """
        Verifies if the data has been tampered with by recreating the hash
        and comparing it to the stored hash.
        """
        recalculated_hash = BlockchainSimulator.generate_hash(data, previous_hash)
        return recalculated_hash == current_hash

blockchain = BlockchainSimulator()
