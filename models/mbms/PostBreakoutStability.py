# models/mbms/PostBreakoutStability.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects whether a breakout was healthy and stable:
    - Small pullback with strong volume support
    - Price holds above previous resistance
    Indicates possible continuation after breakout.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    if len(df) < 10:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Detect breakout over past resistance (10-bar max)
    resistance = df["rate"].rolling(10).max().iloc[-2]
    ltp = df["rate"].iloc[-1]
    held_above = ltp > resistance * 0.98

    # Price did not drop back
    drop = (resistance - ltp) / (resistance + 1e-6)
    stable = drop < 0.02

    # Volume still solid
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].rolling(10).mean().iloc[-1]
    volume_ok = vol_now > 0.8 * vol_avg

    breakout_ok = held_above and stable and volume_ok

    confidence = 85 if breakout_ok else 50
    trap_risk = 0.2 if breakout_ok else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
