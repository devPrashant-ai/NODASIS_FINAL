# models/mbms/WhipsawAvoidanceAI.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    WhipsawAvoidanceAI - Detects volatile back-and-forth price moves with no real direction,
    often used to trap retail in fake moves. Helps avoid entering during instability.
    """
    if df.empty or "rate" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.6,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Calculate price swings
    df["rate_change"] = df["rate"].pct_change()
    df["swing_magnitude"] = df["rate_change"].rolling(window=4, min_periods=2).apply(lambda x: np.std(np.sign(x)))
    df["swing_score"] = df["swing_magnitude"] * 100

    swing_level = df["swing_score"].iloc[-1] if not np.isnan(df["swing_score"].iloc[-1]) else 0

    # High swing = unstable = avoid
    if swing_level > 40:
        confidence = 20
        trap_risk = 0.75
        signal = "Avoid"
    else:
        confidence = 65
        trap_risk = 0.35
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
