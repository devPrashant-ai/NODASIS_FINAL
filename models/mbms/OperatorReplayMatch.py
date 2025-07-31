# models/mbms/OperatorReplayMatch.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Matches current volume + price behavior to past known operator accumulation patterns.
    Detects repetition in absorption, volume wave, and flat price patterns.
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

    if len(df) < 12:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Normalize volume
    df["vol_norm"] = df["quantity"] / (df["quantity"].rolling(10).mean() + 1)
    vol_pattern = df["vol_norm"].iloc[-5:].mean()

    # Flat price range
    price_range = df["rate"].iloc[-5:].max() - df["rate"].iloc[-5:].min()
    range_score = 1 - (price_range / df["rate"].iloc[-5:].mean() + 0.01)

    # Replay match score = high normalized volume + flat price
    match_score = (vol_pattern + range_score) / 2
    confidence = match_score * 100
    trap_risk = 0.2 if match_score > 0.7 else 0.5
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
