# models/mbms/TrapAwareMomentum.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    TrapAwareMomentum - Detects strong upward momentum with caution checks
    for sudden volume surges or reversal traps common in manipulated moves.
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

    # Price and volume trends
    df["rate_return"] = df["rate"].pct_change().rolling(window=3).mean()
    df["vol_change"] = df["quantity"].pct_change().rolling(window=3).mean()

    momentum = df["rate_return"].iloc[-1] if not np.isnan(df["rate_return"].iloc[-1]) else 0
    vol_spike = df["vol_change"].iloc[-1] if not np.isnan(df["vol_change"].iloc[-1]) else 0

    confidence = max(0, momentum * 100)
    trap_risk = 0.7 if vol_spike > 1.5 and momentum < 0.02 else 0.3
    signal = "Buy" if confidence > 60 and trap_risk < 0.5 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
