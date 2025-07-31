# models/mbms/OperatorExitSweep.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects operator exit sweep patterns:
    - Sudden large sell volumes
    - Gradual price decline
    - Usually seen after a price push
    Triggers Sell signal when exit is likely underway.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.6,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    if len(df) < 7:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Price trend: declining
    recent_trend = df["rate"].iloc[-1] - df["rate"].iloc[-5]
    downtrend = recent_trend < -2

    # Large volume spike
    vol_now = df["quantity"].iloc[-1]
    vol_prev_avg = df["quantity"].iloc[-6:-1].mean()
    volume_surge = vol_now > 1.5 * vol_prev_avg

    exiting = downtrend and volume_surge

    confidence = 80 if exiting else 50
    trap_risk = 0.65 if exiting else 0.4
    signal = "Sell" if confidence > 70 and trap_risk > 0.5 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
