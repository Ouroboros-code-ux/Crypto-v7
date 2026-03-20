import pandas as pd
import numpy as np
import os
import sys

REAL_DATA_PATH = "backend/data/transaction_dataset.csv"
OUTPUT_PATH    = "backend/data/transactions_dataset.csv"

def prepare_data():
    print(f"Loading real dataset from: {REAL_DATA_PATH}")
    df = pd.read_csv(REAL_DATA_PATH)

    df.columns = df.columns.str.strip()

    print(f"Original shape: {df.shape}")
    print(f"Fraud rate: {df['FLAG'].mean():.1%}")

    df["tx_amount"] = (
        df["avg val sent"].fillna(0) + df["avg val received"].fillna(0)
    ) / 2.0

    df["time_since_last_tx_seconds"] = (
        df["Avg min between sent tnx"].fillna(0) * 60
    )

    df["degree_centrality"] = (
        df["Unique Sent To Addresses"].fillna(0)
        + df["Unique Received From Addresses"].fillna(0)
    )

    tx_col = None
    for candidate in [
        ,
        ,
    ]:
        if candidate in df.columns:
            tx_col = candidate
            break
    if tx_col is None:
        
        df["historical_tx_count"] = df["Sent tnx"].fillna(0) + df["Received Tnx"].fillna(0)
    else:
        df["historical_tx_count"] = df[tx_col].fillna(0)

    total_out = df["total Ether sent"].fillna(0)
    total_in  = df["total ether received"].fillna(0)
    df["in_out_ratio"] = np.where(
        total_out > 0,
        total_in / total_out,
        total_in          
    )

    df["sent_tnx"]      = df["Sent tnx"].fillna(0)
    df["received_tnx"]  = df["Received Tnx"].fillna(0)
    df["time_diff_mins"] = df["Time Diff between first and last (Mins)"].fillna(0)

    df["is_fraud"] = df["FLAG"].astype(int)

    model_cols = [
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
        ,
    ]

    out = df[model_cols].dropna()

    out = out.copy()
    out["tx_amount"]                  = out["tx_amount"].clip(upper=1e6)
    out["time_since_last_tx_seconds"] = out["time_since_last_tx_seconds"].clip(upper=1e7)
    out["degree_centrality"]          = out["degree_centrality"].clip(upper=5000)
    out["historical_tx_count"]        = out["historical_tx_count"].clip(upper=20000)
    out["in_out_ratio"]               = out["in_out_ratio"].clip(upper=1000)
    out["sent_tnx"]                   = out["sent_tnx"].clip(upper=10000)
    out["received_tnx"]               = out["received_tnx"].clip(upper=10000)
    out["time_diff_mins"]             = out["time_diff_mins"].clip(upper=1e7)

    out = out.round(4)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved {len(out)} rows -> {OUTPUT_PATH}")
    print(out["is_fraud"].value_counts(normalize=True).rename("fraction"))
    print("\nSample rows:")
    print(out.head(5).to_string())

if __name__ == "__main__":
    prepare_data()
    
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from backend.services.ml_model import train_model
    train_model()