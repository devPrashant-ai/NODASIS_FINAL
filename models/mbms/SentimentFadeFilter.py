# models/mbms/SentimentFadeFilter.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SentimentFadeFilter - Detects when initial buying sentiment fades and volume stalls,
    signaling potential weakness or operator reset.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.6,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Look for a spike then drop pattern in volume and rate
    df["rate_change"] = df["rate"].pct_change().fillna(0)
    df["vol_ma"] = df["quantity"].rolling(window=5, min_periods=2).mean()
    df["vol_change"] = df["vol_ma"].pct_change().fillna(0)

    last_rate_change = df["rate_change"].iloc[-1]
    last_vol_change = df["vol_change"].iloc[-1]

    fade_condition = last_rate_change < 0 and last_vol_change < -0.1

    confidence = max(0, (-last_rate_change * -last_vol_change) * 80 if fade_condition else 20)
    trap_risk = 0.7 if fade_condition else 0.3
    signal = "Avoid" if trap_risk > 0.6 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
