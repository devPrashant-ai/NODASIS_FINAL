# models/mbms/BreakoutFailWarning.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects potential breakout failure by analyzing recent high points followed by reversal.
    Looks for sharp upmove followed by low volume pullback — common operator trap.
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

    # Recent high and low
    recent_high = df["rate"].rolling(window=10, min_periods=3).max().iloc[-1]
    current = df["rate"].iloc[-1]
    pullback_pct = (recent_high - current) / recent_high

    # Volume fade after breakout
    df["vol_ma"] = df["quantity"].rolling(window=5).mean()
    vol_drop = (df["vol_ma"].iloc[-3] - df["vol_ma"].iloc[-1]) / (df["vol_ma"].iloc[-3] + 1)

    trap_risk = min(max(pullback_pct + vol_drop, 0), 1)
    confidence = 100 - (trap_risk * 100)

    signal = "Sell" if trap_risk > 0.5 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
