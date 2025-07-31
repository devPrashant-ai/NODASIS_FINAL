# models/mbms/PreBreakoutSuppression.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects pre-breakout suppression:
    - Volume dries up while price holds tight
    - Suggests accumulation phase before breakout
    A classic setup used by operators to hide strength.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.3,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    if len(df) < 10:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Volume suppression
    vol_std = df["quantity"].rolling(7).std().iloc[-1]
    low_volume = vol_std < 100

    # Price tight range
    price_range = df["rate"].rolling(7).max().iloc[-1] - df["rate"].rolling(7).min().iloc[-1]
    tight_range = price_range < 2

    suppression = low_volume and tight_range

    confidence = 80 if suppression else 55
    trap_risk = 0.2 if suppression else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
