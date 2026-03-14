import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import csv

# 8 features — must stay in sync with prepare_real_data.py and analysis.py
EXPECTED_COLS = [
    "tx_amount",
    "time_since_last_tx_seconds",
    "degree_centrality",
    "historical_tx_count",
    "in_out_ratio",
    "sent_tnx",
    "received_tnx",
    "time_diff_mins",
]

def train_model(
    dataset_path: str = "backend/data/transactions_dataset.csv",
    model_path: str   = "backend/data/fraud_model.pkl",
):
    """
    Trains a Random Forest classifier on the real Kaggle dataset
    (or synthetic fallback) to detect fraudulent wallets.
    """
    print(f"Loading dataset from {dataset_path}...")
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print("Dataset not found! Please run prepare_real_data.py first.")
        return

    # Drop rows that are missing any of our expected columns
    available = [c for c in EXPECTED_COLS if c in df.columns]
    missing   = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        print(f"WARNING: missing columns (will default to 0): {missing}")
        for col in missing:
            df[col] = 0.0

    X = df[EXPECTED_COLS]
    y = df["is_fraud"]

    print(f"Dataset size: {len(df)} rows | Fraud rate: {y.mean():.1%}")
    print("Splitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Random Forest Classifier (8 features)...")
    # class_weight='balanced' is critical when fraud cases are a minority
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = clf.predict(X_test)

    print("\n--- Model Evaluation ---\n")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    print("\nFeature importances:")
    for col, imp in sorted(
        zip(EXPECTED_COLS, clf.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {col:35s}: {imp:.4f}")

    # Save the model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)

    print(f"\nModel saved successfully to {model_path}")


def load_and_predict(
    features_dict: dict,
    model_path: str = "backend/data/fraud_model.pkl",
) -> float:
    """
    Loads the trained model and predicts the probability of fraud
    for a single wallet's feature dict.
    """
    try:
        with open(model_path, "rb") as f:
            clf = pickle.load(f)
    except FileNotFoundError:
        print("Model not found! Run prepare_real_data.py first.")
        return 0.0

    df = pd.DataFrame([features_dict])

    # Fill any missing columns with 0 so prediction never crashes
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = 0.0

    df = df[EXPECTED_COLS]

    # Predict probability of class 1 (Fraud)
    prob = clf.predict_proba(df)[0][1]
    return float(prob)


def append_feedback(
    features_dict: dict,
    ai_risk_score: int,
    dataset_path: str = "backend/data/transactions_dataset.csv",
):
    """
    Learns from Gemini API analysis by appending its conclusion back to
    the dataset. Generates is_fraud label based on the ai_risk_score.
    """
    is_fraud = 1 if ai_risk_score >= 50 else 0

    row_data = [features_dict.get(col, 0.0) for col in EXPECTED_COLS]
    row_data.append(is_fraud)

    file_exists = os.path.isfile(dataset_path)
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)

    try:
        with open(dataset_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(EXPECTED_COLS + ["is_fraud"])
            writer.writerow(row_data)
        print(
            f"Appended feedback to dataset: Risk Score {ai_risk_score} -> Fraud Label {is_fraud}"
        )
    except Exception as e:
        print(f"Failed to append ML feedback: {e}")


if __name__ == "__main__":
    train_model()
