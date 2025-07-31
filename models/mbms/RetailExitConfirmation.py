# models/mbms/RetailExitConfirmation.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    RetailExitConfirmation - Detects points where retail participants are exiting,
    often preceding operator accumulation or a reversal.
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

    # Volume and price drop patterns
    df["price_drop"] = df["rate"].pct_change().rolling(window=3).sum()
    df["vol_spike"] = df["quantity"].pct_change().rolling(window=3).mean()

    drop_score = df["price_drop"].iloc[-1]
    vol_score = df["vol_spike"].iloc[-1]

    # Retail exit condition: price drops with volume spikes
    confidence = max(0, (-drop_score * vol_score) * 100)
    trap_risk = 0.2 if drop_score < -0.03 and vol_score > 0.1 else 0.6
    signal = "Buy" if confidence > 65 and trap_risk < 0.3 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
