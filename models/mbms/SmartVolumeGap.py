# models/mbms/SmartVolumeGap.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SmartVolumeGap - Detects unusual volume surges during low price movement,
    suggesting hidden accumulation or stealth entry activity.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Calculate rolling average volume and gap
    df["vol_ma"] = df["quantity"].rolling(window=7, min_periods=3).mean()
    df["gap"] = df["quantity"] / (df["vol_ma"] + 1)

    # Price compression score
    df["range"] = df["rate"].rolling(window=5, min_periods=2).apply(lambda x: x.max() - x.min())
    price_range = df["range"].iloc[-1] if not np.isnan(df["range"].iloc[-1]) else 0.1

    gap_score = df["gap"].iloc[-1]
    compression_score = 1 / (price_range + 0.01)

    confidence = min(gap_score * compression_score * 8, 100)
    trap_risk = 0.3 if price_range < 2 else 0.6
    signal = "Buy" if confidence > 70 and trap_risk < 0.4 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
