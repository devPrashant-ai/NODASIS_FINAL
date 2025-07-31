# models/mbms/VolumeCompressionPressure.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    VolumeCompressionPressure - Detects squeezing volume patterns where
    trade activity compresses before a breakout move, often used by stealth operators.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.45,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Volume compression: declining standard deviation over time
    df["vol_std_3"] = df["quantity"].rolling(window=3, min_periods=2).std()
    df["vol_std_6"] = df["quantity"].rolling(window=6, min_periods=4).std()

    compression = df["vol_std_6"].iloc[-1] - df["vol_std_3"].iloc[-1]
    rate_trend = df["rate"].pct_change().rolling(window=3).mean().iloc[-1]

    if compression > 0 and rate_trend >= 0:
        confidence = min((compression * 20) + (rate_trend * 100), 100)
        trap_risk = 0.25
        signal = "Buy"
    else:
        confidence = 40
        trap_risk = 0.5
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
