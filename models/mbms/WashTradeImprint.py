# models/mbms/WashTradeImprint.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    WashTradeImprint - Detects abnormal matching patterns between buyer and seller,
    indicating possible wash trades designed to manipulate volume and price perception.
    """
    if df.empty or "buyer" not in df.columns or "seller" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.6,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()

    # Detect trades where buyer and seller are the same (wash trade marker)
    df["wash_flag"] = (df["buyer"] == df["seller"]).astype(int)

    wash_count = df["wash_flag"].rolling(window=10, min_periods=3).sum().iloc[-1]
    wash_ratio = wash_count / 10.0

    confidence = max(0, 70 * wash_ratio)
    trap_risk = 0.8 if wash_ratio > 0.3 else 0.4
    signal = "Avoid" if trap_risk > 0.6 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
