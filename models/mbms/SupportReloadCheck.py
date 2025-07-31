# models/mbms/SupportReloadCheck.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SupportReloadCheck - Detects accumulation near support with renewed buying volume,
    signaling potential re-entry by smart money or operators.
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

    # Recent support level and bounce
    df["support"] = df["rate"].rolling(window=6, min_periods=3).min()
    df["is_near_support"] = (df["rate"] <= df["support"] * 1.05).astype(int)

    # Volume confirmation of reload
    df["vol_avg"] = df["quantity"].rolling(window=5, min_periods=2).mean()
    df["vol_boost"] = df["quantity"] > df["vol_avg"] * 1.5

    reload_zone = (df["is_near_support"] & df["vol_boost"]).astype(int)
    reload_score = reload_zone.rolling(window=3).sum().iloc[-1]

    confidence = min(reload_score * 30, 100)
    trap_risk = 0.2 if reload_score >= 2 else 0.5
    signal = "Buy" if confidence >= 60 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
