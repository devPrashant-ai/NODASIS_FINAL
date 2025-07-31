# models/mbms/PullbackSpringEntry.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects spring-like pullbacks:
    - Sharp dip followed by fast bounce
    - Indicates strong demand and operator reentry
    Often a low-risk entry before trend continuation.
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

    if len(df) < 6:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Check if there was a dip then bounce
    dip = df["rate"].iloc[-3] < df["rate"].iloc[-4]
    bounce = df["rate"].iloc[-1] > df["rate"].iloc[-2] > df["rate"].iloc[-3]

    # Confirm with volume
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].iloc[-5:-1].mean()
    vol_confirm = vol_now > vol_avg

    spring = dip and bounce and vol_confirm

    confidence = 82 if spring else 50
    trap_risk = 0.2 if spring else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
