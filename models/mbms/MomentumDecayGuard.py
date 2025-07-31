# models/mbms/MomentumDecayGuard.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects decaying momentum after a strong run.
    - Volume fading
    - Price stalling
    - Higher risk of reversal or sideways trap
    Used to prevent late entries.
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

    # Price movement decaying
    recent_gain = df["rate"].iloc[-1] - df["rate"].iloc[-6]
    price_stalling = abs(recent_gain) < 2.0

    # Volume drop
    recent_vol = df["quantity"].iloc[-1]
    prev_avg_vol = df["quantity"].iloc[-6:-1].mean()
    volume_drop = recent_vol < 0.7 * prev_avg_vol

    decay_detected = price_stalling and volume_drop

    confidence = 40 if decay_detected else 70
    trap_risk = 0.6 if decay_detected else 0.25
    signal = "Hold" if decay_detected else "Buy"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
