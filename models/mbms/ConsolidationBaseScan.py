# models/mbms/ConsolidationBaseScan.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects long-duration sideways consolidation base, typically a precursor to a breakout.
    Focuses on price flatness and stable volume over an extended period.
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

    # Rolling standard deviation over 20 days (price flatness)
    price_std_20 = df["rate"].rolling(window=20).std().iloc[-1]
    vol_std_20 = df["quantity"].rolling(window=20).std().iloc[-1]

    flat_price = price_std_20 < 1.5
    stable_volume = vol_std_20 < 150

    if flat_price and stable_volume:
        confidence = 85
        trap_risk = 0.2
        signal = "Buy"
    elif flat_price:
        confidence = 65
        trap_risk = 0.3
        signal = "Hold"
    else:
        confidence = 40
        trap_risk = 0.5
        signal = "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": confidence,
        "trap_risk": trap_risk,
        "signal": signal,
        "sector": get_sector(symbol)
    }
