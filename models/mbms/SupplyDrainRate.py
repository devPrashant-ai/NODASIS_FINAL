# models/mbms/SupplyDrainRate.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SupplyDrainRate - Detects if available sell-side volume is drying up
    while price remains stable or climbs, suggesting a potential breakout setup.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Calculate volume trend
    df["volume_trend"] = df["quantity"].rolling(window=4, min_periods=2).mean().diff()
    df["rate_change"] = df["rate"].pct_change().rolling(window=3).mean()

    vol_drain = -df["volume_trend"].iloc[-1] if not np.isnan(df["volume_trend"].iloc[-1]) else 0
    price_strength = df["rate_change"].iloc[-1] if not np.isnan(df["rate_change"].iloc[-1]) else 0

    if vol_drain > 0 and price_strength >= 0:
        confidence = min((vol_drain * (1 + price_strength)) * 100, 100)
        trap_risk = 0.2
        signal = "Buy"
    else:
        confidence = 30
        trap_risk = 0.5
        signal = "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
