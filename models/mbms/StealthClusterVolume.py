# models/mbms/StealthClusterVolume.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    StealthClusterVolume - Identifies dense volume bursts in flat price zones,
    suggesting coordinated, non-retail accumulation (operator clustering).
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

    # Calculate moving average and standard deviation of volume
    df["vol_ma"] = df["quantity"].rolling(window=4, min_periods=2).mean()
    df["vol_std"] = df["quantity"].rolling(window=4, min_periods=2).std()
    df["vol_spike"] = (df["quantity"] > (df["vol_ma"] + df["vol_std"])).astype(int)

    # Identify flat price cluster zone
    df["rate_std"] = df["rate"].rolling(window=4, min_periods=2).std()
    df["flat_zone"] = (df["rate_std"] < 1.5).astype(int)

    cluster_zone = (df["vol_spike"] + df["flat_zone"]).rolling(window=3).sum()
    score = cluster_zone.iloc[-1] if not cluster_zone.empty else 0

    confidence = min(score * 20, 100)
    trap_risk = 0.2 if score >= 4 else 0.5
    signal = "Buy" if confidence > 60 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
# models/mbms/StealthClusterVolume.py

import numpy as np
from utils.sector_map import get_sector

def score_bz(df, symbol=None):
    """
    StealthClusterVolume - Identifies dense volume bursts in flat price zones,
    suggesting coordinated, non-retail accumulation (operator clustering).
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

    # Calculate moving average and standard deviation of volume
    df["vol_ma"] = df["quantity"].rolling(window=4, min_periods=2).mean()
    df["vol_std"] = df["quantity"].rolling(window=4, min_periods=2).std()
    df["vol_spike"] = (df["quantity"] > (df["vol_ma"] + df["vol_std"])).astype(int)

    # Identify flat price cluster zone
    df["rate_std"] = df["rate"].rolling(window=4, min_periods=2).std()
    df["flat_zone"] = (df["rate_std"] < 1.5).astype(int)

    cluster_zone = (df["vol_spike"] + df["flat_zone"]).rolling(window=3).sum()
    score = cluster_zone.iloc[-1] if not cluster_zone.empty else 0

    confidence = min(score * 20, 100)
    trap_risk = 0.2 if score >= 4 else 0.5
    signal = "Buy" if confidence > 60 else "Hold"

    return {
        "confidence": round(confidence, 2),
        "trap_risk": round(trap_risk, 2),
        "signal": signal,
        "sector": get_sector(symbol) if symbol else "Unknown"
    }
