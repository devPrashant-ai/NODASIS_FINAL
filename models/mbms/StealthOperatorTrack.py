# models/mbms/StealthOperatorTrack.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    StealthOperatorTrack - Detects hidden operator footprints by analyzing
    repeated volume injections during controlled price zones.
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

    # Volume injection pattern: large volume in small price range
    df["vol_ma"] = df["quantity"].rolling(window=5, min_periods=2).mean()
    df["vol_std"] = df["quantity"].rolling(window=5, min_periods=2).std()
    df["volume_anomaly"] = (df["quantity"] > df["vol_ma"] + 2 * df["vol_std"]).astype(int)

    df["rate_range"] = df["rate"].rolling(window=5, min_periods=2).apply(lambda x: x.max() - x.min())
    df["tight_price"] = (df["rate_range"] < 1.5).astype(int)

    footprint_score = (df["volume_anomaly"] + df["tight_price"]).rolling(window=3).sum().iloc[-1]
    confidence = min(footprint_score * 20, 100)
    trap_risk = 0.2 if footprint_score >= 4 else 0.45
    signal = "Buy" if confidence > 60 and trap_risk < 0.3 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
