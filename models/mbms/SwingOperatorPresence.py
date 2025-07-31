# models/mbms/SwingOperatorPresence.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SwingOperatorPresence - Identifies signs of swing operator activity
    by detecting smooth accumulation waves followed by quick low-volume pullbacks.
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

    # Smooth accumulation: gradual price rise + healthy volume
    df["price_trend"] = df["rate"].rolling(window=5, min_periods=3).mean().diff()
    df["volume_avg"] = df["quantity"].rolling(window=5, min_periods=3).mean()

    # Look for rise with controlled pullback
    price_trend = df["price_trend"].iloc[-1] if not np.isnan(df["price_trend"].iloc[-1]) else 0
    recent_vol = df["quantity"].iloc[-1]
    avg_vol = df["volume_avg"].iloc[-1] if not np.isnan(df["volume_avg"].iloc[-1]) else 1

    pullback_detected = df["rate"].pct_change().iloc[-1] < 0 and recent_vol < avg_vol

    confidence = max(0, price_trend * 100 if price_trend > 0 else 20)
    trap_risk = 0.2 if price_trend > 0 and pullback_detected else 0.5
    signal = "Buy" if confidence > 60 and trap_risk < 0.4 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
