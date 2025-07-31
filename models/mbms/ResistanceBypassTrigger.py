# models/mbms/ResistanceByPassTrigger.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects clean resistance bypass:
    - Price moves above recent resistance smoothly
    - Without hesitation or pullback
    - Volume confirms breakout strength
    Indicates strong operator control and demand.
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

    # Calculate resistance as prior 7-day high
    resistance = df["rate"].rolling(7).max().iloc[-3]
    breakout = df["rate"].iloc[-1] > resistance * 1.02

    # Volume confirms
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].iloc[-10:-1].mean()
    vol_confirm = vol_now > vol_avg * 1.2

    clean_bypass = breakout and vol_confirm

    confidence = 88 if clean_bypass else 55
    trap_risk = 0.15 if clean_bypass else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
