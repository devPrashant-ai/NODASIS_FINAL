# models/mbms/LiquiditySpikeDetector.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects sudden spikes in traded quantity without much price change.
    Indicates a hidden liquidity event — likely operator or large player in action.
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Volume spike logic
    vol_now = df["quantity"].iloc[-1]
    vol_ma = df["quantity"].rolling(window=10).mean().iloc[-1]
    vol_spike = vol_now > 2 * vol_ma

    # Price movement flat
    price_std = df["rate"].rolling(window=5).std().iloc[-1]
    price_stable = price_std < 1.0

    # Final logic
    confidence = 85 if vol_spike and price_stable else 55
    trap_risk = 0.2 if vol_spike and price_stable else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
