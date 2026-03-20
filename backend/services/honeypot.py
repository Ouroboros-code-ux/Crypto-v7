import random
import time

def generate_fake_scan_result(address: str):
    
    risk_score = random.randint(10, 30)
    return {
        "address": address,
        "chain": "ETH",
        "stats": {
            "transaction_count": random.randint(5, 50),
            "total_ether_in": round(random.uniform(0.1, 5.5), 4),
            "total_ether_out": round(random.uniform(0.1, 5.0), 4),
            "last_active": int(time.time()) - random.randint(3600, 86400)
        },
        "analysis": {
            "risk_score": risk_score,
            "risk_level": "LOW",
            "explanation": "Account analysis complete. No significant malicious patterns detected. Forensic layer indicates standard retail behavior.",
            "peeling_chain_detected": False
        },
        "community_flagged": False,
        "transactions": [] 
    }

def generate_fake_report_response():
    
    return {
        "status": "success",
        "msg": "Report received. Pending review by the manual verification team.",
        "verified": False
    }