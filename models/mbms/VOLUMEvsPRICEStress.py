# models/mbms/VOLUMEvsPRICEStress.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    VOLUMEvsPRICEStress - Detects when volume increases without price confirmation,
    signaling stress or manipulation and possible fake breakout attempts.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return {
            "confidence": 0,
            "trap_risk": 0.5,
            "signal": "Hold",
            "sector": get_sector(symbol) if symbol else "Unknown"
        }

    df = df.copy()
    df = df.sort_values(by="date")

    # Price change vs volume surge ratio
    df["rate_change"] = df["rate"].pct_change().rolling(window=3).mean()
    df["vol_change"] = df["quantity"].pct_change().rolling(window=3).mean()

    price_trend = df["rate_change"].iloc[-1] if not np.isnan(df["rate_change"].iloc[-1]) else 0
    volume_trend = df["vol_change"].iloc[-1] if not np.isnan(df["vol_change"].iloc[-1]) else 0

    # Stress = volume goes up but price does not follow
    if volume_trend > 0.3 and price_trend < 0.01:
        confidence = 30
        trap_risk = 0.75
        signal = "Avoid"
    else:
        confidence = 65
        trap_risk = 0.3
        signal = "Hold" if confidence < 70 else "Buy"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
