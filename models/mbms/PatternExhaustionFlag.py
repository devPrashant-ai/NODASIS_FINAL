# models/mbms/PatternExhaustionFlag.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects when a symbol shows signs of exhaustion after repeating a bullish pattern too often.
    - Price fails to make new highs
    - Volume drops at each push
    - Indicates trap risk or reversal incoming
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

    if len(df) < 10:
        return {
            "confidence": 0,
            "trap_risk": 0.45,
            "signal": "Hold",
            "sector": "Unknown"
        }

    highs = df["rate"].rolling(3).max().dropna()
    newer_highs = highs[-3:]

    lower_high = (
        newer_highs.iloc[-1] < newer_highs.iloc[-2] and
        newer_highs.iloc[-2] < newer_highs.iloc[-3]
    )

    # Volume dropping across recent bars
    vol_decline = (
        df["quantity"].iloc[-1] < df["quantity"].iloc[-2] < df["quantity"].iloc[-3]
    )

    exhaustion = lower_high and vol_decline
    confidence = 40 if exhaustion else 75
    trap_risk = 0.6 if exhaustion else 0.3
    signal = "Sell" if trap_risk > 0.5 and confidence < 50 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
