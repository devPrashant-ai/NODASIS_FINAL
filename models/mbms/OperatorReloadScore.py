# models/mbms/OperatorReloadScore.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects operator reload phases:
    - Price dips toward previous cost zone
    - Volume begins to pick up again
    - Indicates second wave of accumulation before breakout
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

    if len(df) < 10:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Simulated cost zone = 10-bar volume-weighted average price (VWAP)
    df["value"] = df["rate"] * df["quantity"]
    vwap_10 = df["value"].rolling(10).sum() / (df["quantity"].rolling(10).sum() + 1e-6)
    last_vwap = vwap_10.iloc[-1]
    ltp = df["rate"].iloc[-1]

    # Volume pressure up
    vol_now = df["quantity"].iloc[-1]
    vol_avg = df["quantity"].rolling(10).mean().iloc[-1]
    volume_rising = vol_now > 1.2 * vol_avg

    near_cost_zone = abs(ltp - last_vwap) / last_vwap < 0.03

    reloading = near_cost_zone and volume_rising

    confidence = 83 if reloading else 55
    trap_risk = 0.2 if reloading else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
