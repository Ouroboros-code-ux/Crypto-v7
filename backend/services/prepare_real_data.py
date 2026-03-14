"""
Script to convert the Kaggle Ethereum Fraud Detection dataset
(transaction_dataset.csv) into the format expected by our ML model,
then retrain the model on the real data.

Real Dataset columns used:
  - FLAG                                      -> is_fraud (label)
  - avg val sent / avg val received           -> tx_amount
  - Avg min between sent tnx                  -> time_since_last_tx_seconds
  - Unique Sent To Addresses + Unique Received From Addresses -> degree_centrality
  - total transactions (including tnx to create contract)    -> historical_tx_count
  - total Ether sent / total ether received   -> in_out_ratio
  - Sent tnx                                  -> sent_tnx       (NEW)
  - Received Tnx                              -> received_tnx   (NEW)
  - Time Diff between first and last (Mins)   -> time_diff_mins (NEW)
"""

import pandas as pd
import numpy as np
import os
import sys

REAL_DATA_PATH = "backend/data/transaction_dataset.csv"
OUTPUT_PATH    = "backend/data/transactions_dataset.csv"

def prepare_data():
    print(f"Loading real dataset from: {REAL_DATA_PATH}")
    df = pd.read_csv(REAL_DATA_PATH)

    # Strip whitespace from all column names to avoid silent NaN bugs
    df.columns = df.columns.str.strip()

    print(f"Original shape: {df.shape}")
    print(f"Fraud rate: {df['FLAG'].mean():.1%}")

    # -------------------------------------------------------
    # Feature mapping
    # -------------------------------------------------------

    # tx_amount: average of avg sent and avg received (in ETH)
    df["tx_amount"] = (
        df["avg val sent"].fillna(0) + df["avg val received"].fillna(0)
    ) / 2.0

    # time_since_last_tx_seconds: Avg min between sent tnx (convert minutes -> seconds)
    df["time_since_last_tx_seconds"] = (
        df["Avg min between sent tnx"].fillna(0) * 60
    )

    # degree_centrality: unique senders + unique receivers
    df["degree_centrality"] = (
        df["Unique Sent To Addresses"].fillna(0)
        + df["Unique Received From Addresses"].fillna(0)
    )

    # historical_tx_count — the column name has no closing parenthesis in Kaggle CSV
    # Try both variants to be safe
    tx_col = None
    for candidate in [
        "total transactions (including tnx to create contract)",
        "total transactions (including tnx to create contract",
    ]:
        if candidate in df.columns:
            tx_col = candidate
            break
    if tx_col is None:
        # Fallback: sum sent + received
        df["historical_tx_count"] = df["Sent tnx"].fillna(0) + df["Received Tnx"].fillna(0)
    else:
        df["historical_tx_count"] = df[tx_col].fillna(0)

    # in_out_ratio: total_in / total_out (guard against division by zero)
    total_out = df["total Ether sent"].fillna(0)
    total_in  = df["total ether received"].fillna(0)
    df["in_out_ratio"] = np.where(
        total_out > 0,
        total_in / total_out,
        total_in          # if nothing went out, ratio = amount received
    )

    # --- NEW FEATURES ---
    df["sent_tnx"]      = df["Sent tnx"].fillna(0)
    df["received_tnx"]  = df["Received Tnx"].fillna(0)
    df["time_diff_mins"] = df["Time Diff between first and last (Mins)"].fillna(0)

    # Label
    df["is_fraud"] = df["FLAG"].astype(int)

    # -------------------------------------------------------
    # Select only model columns and drop rows with NaN
    # -------------------------------------------------------
    model_cols = [
        "tx_amount",
        "time_since_last_tx_seconds",
        "degree_centrality",
        "historical_tx_count",
        "in_out_ratio",
        "sent_tnx",
        "received_tnx",
        "time_diff_mins",
        "is_fraud",
    ]

    out = df[model_cols].dropna()

    # Clip extreme outliers to keep the model general
    out = out.copy()
    out["tx_amount"]                  = out["tx_amount"].clip(upper=1e6)
    out["time_since_last_tx_seconds"] = out["time_since_last_tx_seconds"].clip(upper=1e7)
    out["degree_centrality"]          = out["degree_centrality"].clip(upper=5000)
    out["historical_tx_count"]        = out["historical_tx_count"].clip(upper=20000)
    out["in_out_ratio"]               = out["in_out_ratio"].clip(upper=1000)
    out["sent_tnx"]                   = out["sent_tnx"].clip(upper=10000)
    out["received_tnx"]               = out["received_tnx"].clip(upper=10000)
    out["time_diff_mins"]             = out["time_diff_mins"].clip(upper=1e7)

    # Round to 4 dp for a smaller file
    out = out.round(4)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    out.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved {len(out)} rows -> {OUTPUT_PATH}")
    print(out["is_fraud"].value_counts(normalize=True).rename("fraction"))
    print("\nSample rows:")
    print(out.head(5).to_string())


if __name__ == "__main__":
    prepare_data()
    # Immediately retrain the model
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from backend.services.ml_model import train_model
    train_model()
