# models/mbms/LateVolumeEntry.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects operator-style late-day volume surges where price does not move much,
    indicating stealth buying. Common before breakout.
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
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Compare last bar volume to recent average
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].iloc[-10:-1].mean()
    late_spike = vol_now > 1.5 * vol_avg

    # Price hasn't moved much
    rate_now = df["rate"].iloc[-1]
    rate_prev = df["rate"].iloc[-2]
    price_flat = abs(rate_now - rate_prev) < 1.0

    confidence = 80 if late_spike and price_flat else 50
    trap_risk = 0.15 if price_flat and late_spike else 0.35
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
