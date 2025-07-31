# models/mbms/BIDClusterReentry.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects reentry of stealth operators via BO ID clustering behavior.
    Looks for repeated volume patterns at same price levels with low volatility.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Cluster-like repeated price levels
    cluster_window = df["rate"].round(-1).value_counts().head(3)
    cluster_strength = cluster_window.max() / len(df)

    # Reentry score = high cluster + rising volume
    df["vol_ma"] = df["quantity"].rolling(window=10, min_periods=3).mean()
    vol_boost = df["quantity"].iloc[-1] / (df["vol_ma"].iloc[-1] + 1)

    price_std = df["rate"].rolling(10).std().iloc[-1] or 0.01

    confidence = cluster_strength * vol_boost * 100
    trap_risk = 0.1 if price_std < 1.5 else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
