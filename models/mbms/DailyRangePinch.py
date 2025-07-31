# models/mbms/DailyRangePinch.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects a price pinch — very narrow daily range — indicating coiled energy before a move.
    Works best when paired with steady volume and previous trend buildup.
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

    # Rolling range
    df["high"] = df["rate"].rolling(3).max()
    df["low"] = df["rate"].rolling(3).min()
    df["range"] = df["high"] - df["low"]
    range_pct = (df["range"] / df["rate"]).rolling(3).mean().iloc[-1]

    # Volume consistency
    vol_std = df["quantity"].rolling(5).std().iloc[-1]
    volume_stable = vol_std < 150

    confidence = (1 - range_pct) * 100 if volume_stable else 50
    trap_risk = 0.2 if range_pct < 0.015 else 0.5
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
