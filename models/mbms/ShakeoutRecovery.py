# models/mbms/ShakeoutRecovery.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    ShakeoutRecovery - Detects strong volume spikes after rapid price drops,
    indicating possible operator re-entry or retail flush and bounce.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Volume expansion relative to average
    df["vol_ma"] = df["quantity"].rolling(window=10, min_periods=3).mean()
    df["gap"] = df["quantity"] / (df["vol_ma"] + 1)
    gap_score = df["gap"].iloc[-1] if not df["gap"].empty else 1

    # Price shakeout detection (recent standard deviation)
    price_std = df["rate"].rolling(window=10, min_periods=3).std().iloc[-1]
    price_std = price_std if not np.isnan(price_std) else 0.01
    price_stability = 1 / (price_std + 0.01)

    confidence = gap_score * price_stability * 10
    trap_risk = 0.2 if price_std < 1 else 0.6
    signal = "Buy" if confidence > 75 and trap_risk < 0.3 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
