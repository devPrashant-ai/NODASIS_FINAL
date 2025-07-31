# models/mbms/BreakoutZoneCluster.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects tight consolidation zones near breakout levels.
    If price volatility is low and volume is stable, breakout may be imminent.
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

    # --- Volatility of last 10 bars ---
    price_std = df["rate"].rolling(window=10).std().iloc[-1]
    price_std = price_std if not np.isnan(price_std) else 0.1

    # --- Volume flatness ---
    vol_std = df["quantity"].rolling(window=10).std().iloc[-1]
    vol_std = vol_std if not np.isnan(vol_std) else 1

    # --- Ratio of latest rate to past 10-bar range ---
    max_price = df["rate"].rolling(10).max().iloc[-1]
    min_price = df["rate"].rolling(10).min().iloc[-1]
    range_pct = (max_price - min_price) / (min_price + 1e-6)

    # --- Scoring ---
    tight_cluster = price_std < 1 and vol_std < 100
    confidence = (1 - range_pct) * 100 if tight_cluster else 40
    trap_risk = 0.2 if tight_cluster else 0.5
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
