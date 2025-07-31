# models/mbms/OperatorMoodMonitor.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Gauges the 'mood' of the operator:
    - Accumulation (Buy mood)
    - Exit / Sell pressure (Sell mood)
    - Neutral zone (Hold)
    Based on price + volume coordination, pressure strength, and volatility shift.
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

    if len(df) < 10:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Trend direction
    trend = df["rate"].iloc[-1] - df["rate"].iloc[-6]
    uptrend = trend > 2
    downtrend = trend < -2

    # Volume change
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].iloc[-10:-1].mean()
    vol_spike = vol_now > 1.5 * vol_avg

    # Volatility shift
    vol1 = df["rate"].rolling(5).std().iloc[-1]
    vol2 = df["rate"].rolling(5).std().iloc[-6]
    vol_jump = vol1 > vol2

    # Decision logic
    if uptrend and vol_spike and not vol_jump:
        signal = "Buy"
        confidence = 85
        trap_risk = 0.2
    elif downtrend and vol_spike:
        signal = "Sell"
        confidence = 80
        trap_risk = 0.6
    else:
        signal = "Hold"
        confidence = 60
        trap_risk = 0.4

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": confidence,
        "trap_risk": trap_risk,
        "signal": signal,
        "sector": get_sector(symbol)
    }
