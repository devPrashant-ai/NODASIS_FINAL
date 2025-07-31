# models/mbms/RapidAccumulationBar.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects a single large accumulation bar:
    - Sudden high volume
    - Narrow price movement
    - Strong sign of operator loading in a single session
    """

    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.35,
            "signal": "Hold",
            "sector": "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    if len(df) < 6:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Look at last bar
    last_vol = df["quantity"].iloc[-1]
    avg_vol = df["quantity"].iloc[-6:-1].mean()

    # Narrow price range (absorption)
    price_range = abs(df["rate"].iloc[-1] - df["rate"].iloc[-2])
    narrow_range = price_range < 1.5

    large_volume = last_vol > 1.8 * avg_vol

    accumulation = large_volume and narrow_range

    confidence = 85 if accumulation else 50
    trap_risk = 0.2 if accumulation else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
