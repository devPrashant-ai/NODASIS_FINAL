# models/mbms/GapDownAbsorption.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects gap-down absorption patterns where price drops fast
    but volume rises — signaling strong hidden buying.
    Used to identify early recovery zones before bullish reversal.
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

    # Price change: last vs 3 days ago
    if len(df) < 4:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    rate_now = df["rate"].iloc[-1]
    rate_prev = df["rate"].iloc[-4]
    price_drop = rate_prev - rate_now
    drop_pct = price_drop / (rate_prev + 1e-6)

    # Volume rise
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].rolling(5).mean().iloc[-1]
    vol_boost = vol_now / (vol_avg + 1)

    # Scoring logic
    absorbing = drop_pct > 0.02 and vol_boost > 1.5
    confidence = 85 if absorbing else 45
    trap_risk = 0.2 if absorbing else 0.5
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
