# models/mbms/SlowClimbPredictor.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Calculate rolling return and volume stability
    df["rate_change"] = df["rate"].pct_change().fillna(0)
    df["vol_ma"] = df["quantity"].rolling(window=5, min_periods=2).mean()
    df["vol_std"] = df["quantity"].rolling(window=5, min_periods=2).std()

    avg_climb = df["rate_change"].rolling(window=7, min_periods=3).mean().iloc[-1]
    vol_stability = 1 - (df["vol_std"].iloc[-1] / (df["vol_ma"].iloc[-1] + 1e-3))

    confidence = max(0, avg_climb * vol_stability * 300)
    trap_risk = 0.15 if avg_climb > 0 and vol_stability > 0.5 else 0.5
    signal = "Buy" if confidence > 65 else "Hold"

    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
