# models/mbms/HighFrequencyDipSpotter.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Identifies symbols experiencing multiple small dip attempts with immediate recovery.
    These repeated intraday 'dips' can signal algorithmic accumulation by operators.
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

    if len(df) < 12:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Detect recent dips (price drop and recovery)
    dips = 0
    for i in range(len(df) - 5, len(df) - 1):
        drop = df["rate"].iloc[i] < df["rate"].iloc[i - 1]
        recover = df["rate"].iloc[i + 1] > df["rate"].iloc[i]
        if drop and recover:
            dips += 1

    dip_ratio = dips / 4  # normalize to 0–1
    confidence = dip_ratio * 100
    trap_risk = 0.1 if dips >= 3 else 0.4
    signal = "Buy" if dips >= 3 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
