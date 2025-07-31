# models/mbms/PriceReclaimReversal.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects reclaim reversals:
    - Price drops below key support and then reclaims it
    - Suggests fake breakdown and strong buyer presence
    Often leads to rapid reversal upward.
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

    if len(df) < 8:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Simulate support as rolling min of prior bars
    support = df["rate"].rolling(7).min().iloc[-2]
    ltp = df["rate"].iloc[-1]
    was_below = df["rate"].iloc[-2] < support * 0.99
    reclaimed = ltp > support * 1.01

    # Volume confirms?
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].rolling(7).mean().iloc[-1]
    volume_confirm = vol_now > vol_avg

    reclaiming = was_below and reclaimed and volume_confirm

    confidence = 83 if reclaiming else 50
    trap_risk = 0.2 if reclaiming else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
