# models/mbms/SymbolRotationIndex.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    SymbolRotationIndex - Detects patterns where capital rotates back into a symbol
    after temporary absence, indicating cyclical operator interest or stealth re-entry.
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

    # Measure low volume period followed by recent surge
    df["vol_ma"] = df["quantity"].rolling(window=10, min_periods=4).mean()
    df["vol_recent"] = df["quantity"].rolling(window=3, min_periods=2).mean()
    df["rotation_spike"] = (df["vol_recent"] > df["vol_ma"] * 1.5).astype(int)

    # Detect rotation pattern: low volume to sudden spike
    rotation_score = df["rotation_spike"].rolling(window=3).sum().iloc[-1]
    confidence = min(rotation_score * 30, 100)
    trap_risk = 0.25 if rotation_score >= 2 else 0.5
    signal = "Buy" if confidence >= 60 and trap_risk < 0.4 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
