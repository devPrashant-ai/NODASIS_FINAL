# models/mbms/TrapExitShadow.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    TrapExitShadow - Detects patterns where operators may be exiting during
    price highs with increasing volume and sudden pullbacks, creating exit traps.
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

    # Detect rising price with sharp recent drop
    df["rate_return"] = df["rate"].pct_change().rolling(window=4).mean()
    df["pullback"] = df["rate"].pct_change(periods=1)

    df["vol_spike"] = df["quantity"] / (df["quantity"].rolling(window=4, min_periods=2).mean() + 1e-3)
    pullback = df["pullback"].iloc[-1]
    vol_spike = df["vol_spike"].iloc[-1]
    prior_trend = df["rate_return"].iloc[-2] if len(df) > 2 else 0

    # Operator trap condition: price rise → spike → pullback
    if pullback < -0.015 and vol_spike > 1.4 and prior_trend > 0:
        trap_risk = 0.8
        confidence = 30
        signal = "Avoid"
    else:
        trap_risk = 0.4
        confidence = 60
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
