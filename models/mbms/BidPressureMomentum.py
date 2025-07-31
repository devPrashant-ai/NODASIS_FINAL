# models/mbms/BidPressureMomentum.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects increasing buyer-side pressure through volume momentum buildup.
    Looks for accelerating volume with rising price trend — a sign of strong demand.
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

    # --- Volume momentum over last 3 days ---
    df["vol"] = df["quantity"]
    vol_momentum = df["vol"].diff().rolling(window=3).mean().iloc[-1]

    # --- Price trend over last 5 days ---
    df["price_change"] = df["rate"].diff()
    price_momentum = df["price_change"].rolling(window=5).mean().iloc[-1]

    # --- Combined score ---
    confidence = (max(vol_momentum, 0) + max(price_momentum, 0)) * 10
    trap_risk = 0.3 if price_momentum > 0 and vol_momentum > 0 else 0.6
    signal = "Buy" if confidence > 65 and trap_risk < 0.5 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(min(confidence, 100), 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
