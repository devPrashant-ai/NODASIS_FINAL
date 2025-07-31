# models/mbms/MicroPumpDetector.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects micro pump-and-absorb cycles:
    - Small upward price jumps
    - Followed by sideways absorption
    - Typically a bullish accumulation pattern before real pump
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

    if len(df) < 7:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Recent small upward moves
    pumps = 0
    for i in range(len(df) - 6, len(df) - 1):
        delta = df["rate"].iloc[i + 1] - df["rate"].iloc[i]
        if 0.5 < delta < 3:
            pumps += 1

    absorption = df["rate"].iloc[-1] < df["rate"].iloc[-2]
    confidence = 75 if pumps >= 2 and absorption else 50
    trap_risk = 0.2 if pumps >= 2 else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
