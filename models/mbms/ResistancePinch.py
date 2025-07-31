# models/mbms/ResistancePinch.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    ResistancePinch - Detects tight consolidation just below resistance,
    indicating potential breakout or operator setup.
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

    # Calculate rolling highs and volatility
    df["rolling_high"] = df["rate"].rolling(window=7, min_periods=3).max()
    df["volatility"] = df["rate"].rolling(window=5, min_periods=3).std()
    df["range"] = df["rolling_high"] - df["rate"]

    # Pinch condition: price is close to recent highs with low volatility
    last_range = df["range"].iloc[-1]
    last_vol = df["volatility"].iloc[-1]

    pinch_score = max(0, 1 - last_range / (df["rolling_high"].iloc[-1] + 1e-3))
    stability = max(0, 1 - last_vol / (df["rate"].mean() + 1e-3))

    confidence = (pinch_score + stability) * 50
    trap_risk = 0.6 if last_range < 1 and last_vol > 2 else 0.3
    signal = "Buy" if confidence > 60 and trap_risk < 0.4 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
