import hashlib
import json
from time import time
import ecdsa
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional
import logging

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, signature: Optional[str] = None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_dict(self) -> Dict:
        return {
            : self.sender,
            : self.recipient,
            : self.amount,
            : self.signature
        }
        
    def hash_tx(self) -> str:
        
        tx_dict = {
            : self.sender,
            : self.recipient,
            : self.amount,
        }
        tx_string = json.dumps(tx_dict, sort_keys=True).encode()
        return hashlib.sha256(tx_string).hexdigest()
        
    def verify_signature(self) -> bool:
        if self.sender == "0": 
            return True
            
        if not self.signature:
            return False
            
        try:
            public_key_bytes = bytes.fromhex(self.sender)
            vk = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)
            tx_hash_bytes = self.hash_tx().encode()
            return vk.verify(bytes.fromhex(self.signature), tx_hash_bytes)
        except Exception as e:
            logging.error(f"Signature verification failed for tx {self.hash_tx()}: {e}")
            return False

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Transaction], proof: int, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def get_hash(self) -> str:
        
        block_dict = {
            : self.index,
            : self.timestamp,
            : [tx.to_dict() for tx in self.transactions],
            : self.proof,
            : self.previous_hash
        }
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        
    def to_dict(self) -> Dict:
        return {
            : self.index,
            : self.timestamp,
            : [tx.to_dict() for tx in self.transactions],
            : self.proof,
            : self.previous_hash,
            : self.get_hash()
        }

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []
        self.nodes = set()
        
        self.ml_predictor = None

        self.new_block(previous_hash='1', proof=100)

    def register_ml_predictor(self, predictor_func):
        
        self.ml_predictor = predictor_func

    def register_node(self, address: str):
        
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def new_block(self, proof: int, previous_hash: Optional[str] = None) -> Block:
        
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.chain[-1].get_hash(),
        )

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float, signature: str) -> int:
        
        tx = Transaction(sender, recipient, amount, signature)
        
        if not tx.verify_signature():
            logging.warning(f"Rejected transaction: Invalid signature from {sender}")
            return -1
            
        if self.ml_predictor and sender != "0": 
            try:
                fraud_prob = self.ml_predictor(tx.to_dict())
                if fraud_prob > 0.90:  
                    logging.warning(f"Rejected transaction: ML detected high fraud probability ({fraud_prob*100:.2f}%)")
                    return -1
            except Exception as e:
                logging.error(f"ML Predictor error: {e}")
                
        self.current_transactions.append(tx)
        return self.last_block.index + 1

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof: int, proof: int, last_hash: str) -> bool:
        
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def proof_of_work(self, last_block: Block) -> int:
        
        last_proof = last_block.proof
        last_hash = last_block.get_hash()

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
                    
        for tx in self.current_transactions:
            if tx.recipient == address:
                balance += tx.amount
            if tx.sender == address:
                balance -= tx.amount
                
        return balance

    def generate_wallet(self) -> Dict[str, str]:
        
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        return {
            : sk.to_string().hex(),
            : vk.to_string().hex() 
        }