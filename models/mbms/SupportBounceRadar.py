# models/mbms/SupportBounceRadar.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SupportBounceRadar - Detects price action bouncing near known support zones
    with volume confirmation, indicating entry opportunity after correction.
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

    # Support = previous 7-day low
    df["support_zone"] = df["rate"].rolling(window=7, min_periods=3).min()
    df["bounce_strength"] = (df["rate"] - df["support_zone"]) / (df["support_zone"] + 1e-3)
    df["volume_ratio"] = df["quantity"] / (df["quantity"].rolling(window=5, min_periods=2).mean() + 1e-3)

    recent_bounce = df["bounce_strength"].iloc[-1]
    recent_vol = df["volume_ratio"].iloc[-1]

    if 0 < recent_bounce < 0.03 and recent_vol > 1.2:
        confidence = min(recent_vol * 90, 100)
        trap_risk = 0.25
        signal = "Buy"
    else:
        confidence = 25
        trap_risk = 0.5
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
