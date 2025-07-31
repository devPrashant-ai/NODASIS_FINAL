# models/mbms/OperatorFootprintScan.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects operator footprints based on repeated volume clusters,
    price defense zones, and low volatility absorption behavior.
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

    # Clustered volume at price zones
    rounded_prices = df["rate"].round(-1)
    top_clusters = rounded_prices.value_counts().head(2)
    cluster_ratio = top_clusters.sum() / len(df)

    # Volatility
    price_std = df["rate"].rolling(10).std().iloc[-1]
    low_vol = price_std < 1.2

    footprint_detected = cluster_ratio > 0.4 and low_vol

    confidence = 88 if footprint_detected else 55
    trap_risk = 0.2 if footprint_detected else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
