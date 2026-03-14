from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

from ..services.blockchain_core import Blockchain
from ..services.ml_model import load_and_predict
from ..limiter import limiter
from .auth import get_current_user

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

# Instantiate the global blockchain object
blockchain = Blockchain()
blockchain.register_ml_predictor(load_and_predict)

class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float
    signature: str

class NodeRegisterRequest(BaseModel):
    nodes: List[str]

@router.get("/chain")
def get_chain():
    """
    Returns the full blockchain
    """
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return response

@router.post("/transactions/new")
def new_transaction(tx: TransactionRequest, current_user = Depends(get_current_user)):
    """
    Adds a new transaction to the mempool
    """
    index = blockchain.new_transaction(tx.sender, tx.recipient, tx.amount, tx.signature)
    
    if index == -1:
        raise HTTPException(status_code=400, detail="Transaction rejected: Invalid signature or ML flagged as fraud")

    return {"message": f"Transaction will be added to Block {index}"}

@router.get("/mine")
def mine(current_user = Depends(get_current_user)):
    """
    Mines a new block
    """
    if not blockchain.current_transactions:
        return {"message": "No transactions to mine", "block": None}
        
    last_block = blockchain.last_block
    
    # Run Proof of Work
    proof = blockchain.proof_of_work(last_block)

    # Reward the miner (sender "0" signifies a new coin minted)
    # We will just reward to a default node address for this demo
    node_identifier = "node_miner_1" 
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        signature="" # Coinbase tx doesn't need a signature
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.last_block.get_hash()
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': [tx.to_dict() for tx in block.transactions],
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    return response

@router.get("/balance/{address}")
def get_balance(address: str):
    """
    Gets the balance of a given address
    """
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance}

@router.get("/keys/generate")
def generate_keys(current_user = Depends(get_current_user)):
    """
    Utility to generate a new key pair for testing
    """
    keys = blockchain.generate_wallet()
    return keys
