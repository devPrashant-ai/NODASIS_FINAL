# models/mbms/HighBaseShakeoutAlert.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects shakeout patterns at high price bases:
    - Sudden dip and recovery
    - High volume on the dip
    Indicates operator cleaning weak hands before push.
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

    if len(df) < 5:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Last 5 bars
    recent = df.iloc[-5:]
    price_range = recent["rate"].max() - recent["rate"].min()
    dip_detected = (recent["rate"].iloc[-2] < recent["rate"].mean()) and (recent["rate"].iloc[-1] > recent["rate"].mean())
    vol_spike = recent["quantity"].iloc[-2] > recent["quantity"].mean() * 1.5

    shakeout = dip_detected and vol_spike and price_range > 2

    confidence = 80 if shakeout else 50
    trap_risk = 0.15 if shakeout else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }

