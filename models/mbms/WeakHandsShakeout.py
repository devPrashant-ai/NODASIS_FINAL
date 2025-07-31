# models/mbms/WeakHandsShakeout.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    WeakHandsShakeout - Detects price drops with panic volume, followed by strong rebounds,
    indicating weak-hand exit and operator absorption.
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

    # Detect a large drop then bounce
    df["rate_change"] = df["rate"].pct_change()
    df["vol_ma"] = df["quantity"].rolling(window=5, min_periods=2).mean()
    df["vol_spike"] = df["quantity"] > df["vol_ma"] * 1.5

    drop = df["rate_change"].rolling(window=2).sum().iloc[-2] if len(df) > 2 else 0
    bounce = df["rate_change"].iloc[-1]
    panic_vol = df["vol_spike"].iloc[-2] if len(df) > 2 else False

    if drop < -0.02 and bounce > 0.015 and panic_vol:
        confidence = min((abs(drop) + bounce) * 300, 100)
        trap_risk = 0.25
        signal = "Buy"
    else:
        confidence = 40
        trap_risk = 0.45
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
