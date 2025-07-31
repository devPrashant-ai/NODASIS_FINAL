# models/mbms/ExitBeforeDumpSignal.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects signs that operators are preparing to dump:
    - Sudden high volume spikes
    - Price starts to flatten or drop
    - Last-minute selling pressure after accumulation
    Generates a Sell signal before a likely dump.
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

    # Last 5-day trend
    rate_change = df["rate"].diff().rolling(5).mean().iloc[-1]
    down_trend = rate_change < -0.5

    # Volume spike on recent bar
    vol_ma = df["quantity"].rolling(10).mean().iloc[-1]
    vol_now = df["quantity"].iloc[-1]
    spike = vol_now > 2 * vol_ma

    # Price flattening
    std_price = df["rate"].rolling(5).std().iloc[-1]
    flat = std_price < 1

    # Combined logic
    confidence = 90 if spike and down_trend else 55
    trap_risk = 0.6 if spike and flat else 0.3
    signal = "Sell" if confidence > 70 and trap_risk > 0.4 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
