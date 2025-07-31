# models/mbms/LTPvsVWAPMagnet.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects LTP vs VWAP proximity — if LTP is tightly orbiting VWAP, it can act like a magnet.
    Suggests controlled trading zone and potential for a directional move.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.3,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Calculate VWAP
    df["value"] = df["rate"] * df["quantity"]
    total_value = df["value"].sum()
    total_volume = df["quantity"].sum()
    vwap = total_value / total_volume if total_volume else df["rate"].mean()

    ltp = df["rate"].iloc[-1]
    gap = abs(ltp - vwap) / (vwap + 1e-6)

    # Magnet behavior: small gap, stable volume
    gap_score = 1 - gap
    stable_volume = df["quantity"].rolling(5).std().iloc[-1] < 200

    confidence = gap_score * 100 if stable_volume else 60
    trap_risk = 0.2 if gap < 0.01 else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
