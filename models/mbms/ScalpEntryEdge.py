# models/mbms/ScalpEntryEdge.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    ScalpEntryEdge - Detects fast pullbacks with recovery potential for scalping.
    Looks for short-term dip followed by volume spike as a bounce signal.
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

    # Detect short-term dip
    df["rate_change"] = df["rate"].pct_change().fillna(0)
    df["bounce"] = df["rate_change"].rolling(window=2).sum()
    df["volume_ma"] = df["quantity"].rolling(window=3).mean().fillna(1)
    df["vol_ratio"] = df["quantity"] / df["volume_ma"]

    recent_bounce = df["bounce"].iloc[-1]
    vol_ratio = df["vol_ratio"].iloc[-1]

    # Good scalp entry: slight recovery and strong volume
    if recent_bounce > 0 and vol_ratio > 1.5:
        confidence = min(recent_bounce * vol_ratio * 150, 100)
        trap_risk = 0.25
        signal = "Buy"
    else:
        confidence = 20
        trap_risk = 0.5
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
