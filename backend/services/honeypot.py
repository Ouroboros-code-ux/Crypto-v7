import random
import time

def generate_fake_scan_result(address: str):
    
    risk_score = random.randint(10, 30)
    return {
        : address,
        : "ETH",
        : {
            : random.randint(5, 50),
            : round(random.uniform(0.1, 5.5), 4),
            : round(random.uniform(0.1, 5.0), 4),
            : int(time.time()) - random.randint(3600, 86400)
        },
        : {
            : risk_score,
            : "LOW",
            : "Account analysis complete. No significant malicious patterns detected. Forensic layer indicates standard retail behavior.",
            : False
        },
        : False,
        : [] 
    }

def generate_fake_report_response():
    
    return {
        : "success",
        : "Report received. Pending review by the manual verification team.",
        : False
    }