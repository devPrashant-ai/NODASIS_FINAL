# models/mbms/ReversalAbsorption.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df):
    """
    Detects strong absorption at the bottom of a dip:
    - Price shows minor bounce
    - Volume increases steadily
    - Indicates hidden accumulation for reversal
    Often used by operators to reload before trend flip.
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

    if len(df) < 6:
        return {
            "confidence": 0,
            "trap_risk": 0.4,
            "signal": "Hold",
            "sector": "Unknown"
        }

    # Dip + bounce
    dip = df["rate"].iloc[-3] < df["rate"].iloc[-4]
    bounce = df["rate"].iloc[-1] > df["rate"].iloc[-2]

    # Volume climbing
    vol_up = df["quantity"].iloc[-1] > df["quantity"].iloc[-2] > df["quantity"].iloc[-3]

    reversal_absorb = dip and bounce and vol_up

    confidence = 80 if reversal_absorb else 50
    trap_risk = 0.2 if reversal_absorb else 0.4
    signal = "Buy" if confidence > 70 and trap_risk < 0.3 else "Hold"

    symbol = df["symbol"].iloc[0] if "symbol" in df.columns else "UNKNOWN"
    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol)
    }
