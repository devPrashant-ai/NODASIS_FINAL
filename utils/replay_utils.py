# utils/replay_utils.py

import numpy as np

def calculate_readiness_score(df):
    """
    Estimate readiness score based on volume and price accumulation behavior.
    Higher score means more likely operator is preparing to move.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return 0.0

    df = df.copy()
    df = df.sort_values(by="date")

    # Moving volume ratio
    df["vol_ma"] = df["quantity"].rolling(window=10, min_periods=3).mean()
    df["vol_ratio"] = df["quantity"] / (df["vol_ma"] + 1)

    # Price squeeze: std dev of rate
    price_std = df["rate"].rolling(window=10, min_periods=3).std().iloc[-1]
    price_std = price_std if not np.isnan(price_std) else 0.01

    latest_ratio = df["vol_ratio"].iloc[-1] if not df["vol_ratio"].empty else 1

    # Final score = more volume + tight price range
    readiness = latest_ratio / (price_std + 0.01)
    readiness = np.clip(readiness, 0, 10)

    return round(readiness, 2)
