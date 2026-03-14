import json
import logging
import sqlite3
import google.generativeai as genai
from typing import List, Optional, Tuple

from ..config import DB_NAME, GEMINI_API_KEY, MIXER_ADDRESSES
from ..internal_types import ScanResponse, WalletStats, AnalysisResult
from .ml_model import load_and_predict, append_feedback
import time

logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def find_rapid_outs(transactions: List[dict], address: str) -> bool:
    if not transactions:
        return False
    
    outgoing = [
        tx for tx in transactions 
        if tx.get("from", "").lower() == address.lower() 
        and float(tx.get("value", 0)) > 0
    ]
    
    if len(outgoing) < 3:
        return False
    
    outgoing.sort(key=lambda x: int(x.get("timeStamp", 0)))
    
    chain_count = 0
    last_time = 0
    last_val = 0
    
    for i, tx in enumerate(outgoing):
        curr_time = int(tx.get("timeStamp", 0))
        try:
            val = float(tx.get("value", 0))
        except (ValueError, TypeError):
            continue
        
        if i == 0:
            last_time = curr_time
            last_val = val
            chain_count = 1
            continue
            
        time_diff = curr_time - last_time
        val_diff_ratio = abs(val - last_val) / (last_val + 0.0001)
        
        if time_diff < 3600 and val_diff_ratio < 0.2:
            chain_count += 1
        else:
            chain_count = 1
            
        last_time = curr_time
        last_val = val
        
        if chain_count >= 3:
            return True
            
    return False

def analyze_wallet(address: str, transactions: List[dict], chain: str, db: Optional[sqlite3.Connection] = None) -> ScanResponse:
    currency_symbol = "MATIC" if chain == "POLYGON" else "ETH"
    
    community_flag = False
    community_reason = ""
    if db:
        from sqlalchemy import text
        result = db.execute(text("SELECT reason FROM reports WHERE address=:addr"), {"addr": address.lower()})
        row = result.fetchone()
        if row:
            community_flag = True
            community_reason = row[0]

    tx_count = len(transactions)
    total_in = 0.0
    total_out = 0.0
    unique_partners = set()
    tornado_interactions = False
    
    clean_txs = []
    tx_summary_lines = [] 

    for tx in transactions:
        try:
            val = float(tx.get("value", 0)) / 10**18
        except (ValueError, TypeError):
            val = 0.0
            
        frm = tx.get("from", "").lower()
        to = tx.get("to", "").lower()
        
        if to == address.lower():
            total_in += val
            unique_partners.add(frm)
            direction = "IN"
        else:
            total_out += val
            unique_partners.add(to)
            direction = "OUT"
        
        if frm in MIXER_ADDRESSES or to in MIXER_ADDRESSES:
            tornado_interactions = True

        try:
            timestamp = int(tx.get('timeStamp', 0))
            hash_str = tx.get('hash', 'unknown')
            
            clean_txs.append({
                "hash": hash_str,
                "timestamp": timestamp,
                "value": round(val, 5),
                "from": frm,
                "to": to,
                "direction": direction
            })
            
            tx_summary_lines.append(
                f"- Tx {hash_str[:10]}...: {val:.4f} {currency_symbol} from {frm[:8]} to {to[:8]}"
            )
        except Exception:
            pass

    peeling_detected = find_rapid_outs(transactions, address)

    # Calculate ML Features (8 features — must match ml_model.py EXPECTED_COLS)
    avg_tx_amount = (total_in + total_out) / (tx_count if tx_count > 0 else 1)

    time_since_last = 0
    first_tx_time   = 0
    last_tx_time    = 0
    if clean_txs:
        timestamps    = [t["timestamp"] for t in clean_txs]
        last_tx_time  = max(timestamps)
        first_tx_time = min(timestamps)
        time_since_last = int(time.time()) - last_tx_time

    in_out_ratio = (total_in / total_out) if total_out > 0 else total_in

    # Count direction-split transaction counts
    sent_tnx     = sum(1 for tx in clean_txs if tx["direction"] == "OUT")
    received_tnx = sum(1 for tx in clean_txs if tx["direction"] == "IN")

    # Time span between first and last transaction in minutes
    time_diff_mins = (last_tx_time - first_tx_time) / 60.0 if clean_txs else 0.0

    ml_features = {
        "tx_amount":                  avg_tx_amount,
        "time_since_last_tx_seconds": time_since_last,
        "degree_centrality":          len(unique_partners),
        "historical_tx_count":        tx_count,
        "in_out_ratio":               in_out_ratio,
        "sent_tnx":                   sent_tnx,
        "received_tnx":               received_tnx,
        "time_diff_mins":             time_diff_mins,
    }

    # 1. Run ML Prediction
    fraud_prob = load_and_predict(ml_features)
    risk_score = int(fraud_prob * 100)
    risk_factors = []

    if community_flag:
        risk_score = max(risk_score, 100)
        risk_factors.append(f"Flagged by community: {community_reason}")
    
    if fraud_prob > 0.8:
        risk_factors.append(f"Local ML Model detected a high fraud probability ({risk_score}%) based on transaction patterns.")
    elif fraud_prob > 0.4:
         risk_factors.append(f"Local ML Model detected suspicious patterns ({risk_score}%).")

    if tornado_interactions:
        # Mixer interaction is still a solid heuristic flag
        risk_score = max(risk_score, 75)
        risk_factors.append("Interacted with crypto mixers")

    if risk_factors:
        explanation = f"AI Service Unavailable. Local ML Detection: {'; '.join(risk_factors)} Note: This is an automatically generated static heuristic analysis."
    else:
        explanation = f"AI Service Unavailable. The local ML model evaluated the transaction parameters and predicted this wallet is generally safe, scoring it at {risk_score}%."
        
    risk_level = "SAFE"
    if risk_score > 75: risk_level = "HIGH RISK"
    elif risk_score > 40: risk_level = "WARNING"

    # 2. Gemini Explanation (Optional Fallback / Enhancer)
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            
            prompt = f"""
            Analyze this {chain} wallet: {address}
            
            AI Model Report:
            - Model Risk Score: {risk_score}/100
            - Flags: {risk_factors}
            - Features: {ml_features}
            
            Stats:
            - Txs: {tx_count}
            - In: {total_in:.2f} {currency_symbol}
            - Out: {total_out:.2f} {currency_symbol}
            
            Recent Activity:
            {chr(10).join(tx_summary_lines[:15])}
            
            Task:
            Review the heuristics and transaction history. 
            Provide a more detailed risk assessment and explanation.
            
            Return JSON:
            {{
                "risk_score": (int 0-100, you can adjust the heuristic score),
                "risk_level": "(SAFE, WARNING, HIGH RISK)",
                "explanation": "concise, professional summary"
            }}
            """
            
            result = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            ai_data = json.loads(result.text)
            
            if ai_data.get("risk_score") is not None:
                ai_score = int(ai_data["risk_score"])
                risk_score = ai_score
            
            if ai_data.get("explanation"):
                explanation = ai_data.get("explanation")
            
            if ai_data.get("risk_level"):
                risk_level = ai_data.get("risk_level")
                
            # ML Feedback Loop execution
            logger.info(f"Appending Gemini feedback to dataset. Original local ML={fraud_prob*100:.2f}%, Gemini={ai_score}%")
            append_feedback(ml_features, ai_score)

        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")

    return ScanResponse(
        address=address, 
        chain=chain, 
        stats=WalletStats(
            transaction_count=tx_count,
            total_ether_in=round(total_in, 4),
            total_ether_out=round(total_out, 4),
            unique_interactions=len(unique_partners),
            tornado_cash_detected=tornado_interactions
        ), 
        analysis=AnalysisResult(
            risk_score=min(risk_score, 100),
            risk_level=risk_level,
            explanation=explanation
        ), 
        transactions=clean_txs, 
        peeling_chain_detected=peeling_detected, 
        community_flagged=community_flag
    )
