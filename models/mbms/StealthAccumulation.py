# models/mbms/StealthAccumulation.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    StealthAccumulation - Detects low-volatility price zones with
    steady volume, signaling possible silent operator accumulation.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Steady volume with minimal price movement
    df["vol_std"] = df["quantity"].rolling(window=5, min_periods=3).std()
    df["vol_ma"] = df["quantity"].rolling(window=5, min_periods=3).mean()
    df["vol_steady"] = 1 - (df["vol_std"] / (df["vol_ma"] + 1))

    df["price_range"] = df["rate"].rolling(window=5, min_periods=3).apply(lambda x: x.max() - x.min())
    df["tight_zone"] = 1 - (df["price_range"] / (df["rate"].mean() + 1))

    steady = df["vol_steady"].iloc[-1]
    tight = df["tight_zone"].iloc[-1]

    confidence = max(0, (steady + tight) * 50)
    trap_risk = 0.2 if tight > 0.6 and steady > 0.6 else 0.45
    signal = "Buy" if confidence > 65 and trap_risk < 0.4 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
