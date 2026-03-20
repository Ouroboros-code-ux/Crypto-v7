import re
import time
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from ..internal_types import ScanResponse
from ..limiter import limiter
from ..config import CACHE_DURATION
from ..database import get_db
from ..services.blockchain import fetch_chain_history
from ..services.analysis import analyze_wallet
from ..services.graph import build_graph_data

from .auth import get_optional_user

router = APIRouter()
scan_cache = {}

@router.get("/scan")
@limiter.limit("5/minute")
def scan_address(request: Request, address: str, db: Session = Depends(get_db), current_user = Depends(get_optional_user)):

    if not address or not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
        
    if address in scan_cache:
        timestamp, cached_response = scan_cache[address]
        if time.time() - timestamp < CACHE_DURATION:
            return cached_response
    
    chain = "ETH"
    transactions = fetch_chain_history(address, "ETH")
    
    if not transactions:
        poly_txs = fetch_chain_history(address, "POLYGON")
        if poly_txs:
            chain = "POLYGON"
            transactions = poly_txs

    response = analyze_wallet(address, transactions, chain, db)
    scan_cache[address] = (time.time(), response)
    
    return response

@router.get("/graph")
@limiter.limit("5/minute")
def get_graph_data(request: Request, address: str, chain: str = "ETH", current_user = Depends(get_optional_user)):

    if not address or not re.match(r"^0x[a-fA-F0-9]{40}$", address):
         raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    
    return build_graph_data(address, chain)