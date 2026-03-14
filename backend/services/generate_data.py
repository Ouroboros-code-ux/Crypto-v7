import pandas as pd
import numpy as np
import random
import os

def generate_dataset(num_samples: int = 5000, output_path: str = "transactions_dataset.csv"):
    """
    Generates a synthetic dataset of cryptocurrency transactions for training an ML model.
    It simulates two types of users:
    - Label 0 (Safe): Normal users, exchanges, random transfers.
    - Label 1 (Fraud): Scammers, wash trading, peeling chains, rapid money movement.
    """
    data = []
    
    print(f"Generating {num_samples} synthetic transactions...")
    
    for _ in range(num_samples):
        # 15% chance of being a fraudulent transaction
        is_fraud = 1 if random.random() < 0.15 else 0
        
        # Base features
        tx_amount = max(0.001, np.random.lognormal(mean=0.5, sigma=1.5))
        
        if is_fraud:
            # Fraud profile: Often huge amounts or tiny wash-trading amounts
            if random.random() < 0.5:
                tx_amount = tx_amount * 10 
            else:
                tx_amount = max(0.0001, tx_amount * 0.01)
                
            # Fraud characteristics
            time_since_last_tx = max(1, int(np.random.exponential(scale=300))) # Very rapid
            degree_centrality = random.randint(1, 5) # Usually moving entirely to new wallets or mixing
            historical_tx_count = random.randint(1, 20) # Burner wallets
            in_out_ratio = random.uniform(0.9, 1.1) # Money comes in and goes right out
            
        else:
            # Safe profile: Standard distributions
            time_since_last_tx = max(100, int(np.random.exponential(scale=86400))) # Normal daily usage
            degree_centrality = random.randint(1, 150) # Exchanges or active users
            historical_tx_count = random.randint(5, 500)
            in_out_ratio = random.uniform(0.1, 5.0) # Varies wildly for normal users
            
        row = {
            "tx_amount": round(tx_amount, 4),
            "time_since_last_tx_seconds": time_since_last_tx,
            "degree_centrality": degree_centrality,
            "historical_tx_count": historical_tx_count,
            "in_out_ratio": round(in_out_ratio, 4),
            "is_fraud": is_fraud
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Dataset generated and saved to {output_path}")
    print(df['is_fraud'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_dataset(output_path="backend/data/transactions_dataset.csv")
