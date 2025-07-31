# models/mbms/EntryWithExitBlock.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects stealth entry patterns where price rises slowly,
    but operator prevents exits using volume suppression or sideway traps.
    Ideal for early Buy signal before breakout.
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

    # Look for slow price increase over 7 days
    price_trend = df["rate"].iloc[-1] - df["rate"].iloc[-7] if len(df) >= 7 else 0
    price_up = price_trend > 2

    # Volume suppression at highs
    high_price = df["rate"].rolling(5).max().iloc[-1]
    high_volume = df[df["rate"] >= high_price * 0.99]["quantity"].mean()
    normal_volume = df["quantity"].rolling(5).mean().iloc[-1]
    exit_block = high_volume < (0.5 * normal_volume)

    confidence = 85 if price_up and exit_block else 50
    trap_risk = 0.2 if price_up and exit_block else 0.45
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
