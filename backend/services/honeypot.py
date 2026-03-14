import random
import time

def generate_fake_scan_result(address: str):
    """
    Generates a realistic-looking but fake scan response for unauthorized probing.
    """
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
        "transactions": [] # Don't return real txs to save bandwidth and obfuscate
    }

def generate_fake_report_response():
    """
    Returns a generic success message for unauthorized report attempts.
    """
    return {
        "status": "success",
        "msg": "Report received. Pending review by the manual verification team.",
        "verified": False
    }
