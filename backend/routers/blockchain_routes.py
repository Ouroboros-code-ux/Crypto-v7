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
    
    response = {
        "chain": [block.to_dict() for block in blockchain.chain],
        "length": len(blockchain.chain),
    }
    return response

@router.post("/transactions/new")
def new_transaction(tx: TransactionRequest, current_user = Depends(get_current_user)):
    
    index = blockchain.new_transaction(tx.sender, tx.recipient, tx.amount, tx.signature)
    
    if index == -1:
        raise HTTPException(status_code=400, detail="Transaction rejected: Invalid signature or ML flagged as fraud")

    return {"message": f"Transaction will be added to Block {index}"}

@router.get("/mine")
def mine(current_user = Depends(get_current_user)):
    
    if not blockchain.current_transactions:
        return {"message": "No transactions to mine", "block": None}
        
    last_block = blockchain.last_block
    
    proof = blockchain.proof_of_work(last_block)

    node_identifier = "node_miner_1" 
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        signature="" 
    )

    previous_hash = blockchain.last_block.get_hash()
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "New Block Forged",
        "index": block.index,
        "transactions": [tx.to_dict() for tx in block.transactions],
        "proof": block.proof,
        "previous_hash": block.previous_hash,
    }
    return response

@router.get("/balance/{address}")
def get_balance(address: str):
    
    balance = blockchain.get_balance(address)
    return {"address": address, "balance": balance}

@router.get("/keys/generate")
def generate_keys(current_user = Depends(get_current_user)):
    
    keys = blockchain.generate_wallet()
    return keys