import pandas as pd
import numpy as np
import random
import os

def generate_dataset(num_samples: int = 5000, output_path: str = "transactions_dataset.csv"):
    
    data = []
    
    print(f"Generating {num_samples} synthetic transactions...")
    
    for _ in range(num_samples):
        
        is_fraud = 1 if random.random() < 0.15 else 0
        
        tx_amount = max(0.001, np.random.lognormal(mean=0.5, sigma=1.5))
        
        if is_fraud:
            
            if random.random() < 0.5:
                tx_amount = tx_amount * 10 
            else:
                tx_amount = max(0.0001, tx_amount * 0.01)
                
            time_since_last_tx = max(1, int(np.random.exponential(scale=300))) 
            degree_centrality = random.randint(1, 5) 
            historical_tx_count = random.randint(1, 20) 
            in_out_ratio = random.uniform(0.9, 1.1) 
            
        else:
            
            time_since_last_tx = max(100, int(np.random.exponential(scale=86400))) 
            degree_centrality = random.randint(1, 150) 
            historical_tx_count = random.randint(5, 500)
            in_out_ratio = random.uniform(0.1, 5.0) 
            
        row = {
            : round(tx_amount, 4),
            : time_since_last_tx,
            : degree_centrality,
            : historical_tx_count,
            : round(in_out_ratio, 4),
            : is_fraud
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Dataset generated and saved to {output_path}")
    print(df['is_fraud'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_dataset(output_path="backend/data/transactions_dataset.csv")