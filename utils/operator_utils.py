# utils/operator_utils.py

import pandas as pd
from collections import defaultdict

def detect_operator_cost(df):
    """
    Estimate operator accumulation price using volume-weighted price from top trades.
    """
    if df.empty or "rate" not in df.columns or "quantity" not in df.columns:
        return 0.0

    df = df.copy()
    df = df.sort_values(by="quantity", ascending=False)
    top_n = max(5, int(len(df) * 0.2))
    top_df = df.head(top_n)

    try:
        vwap = (top_df["rate"] * top_df["quantity"]).sum() / top_df["quantity"].sum()
    except ZeroDivisionError:
        vwap = df["rate"].mean()

    return vwap

def detect_operator_behavior(floor_data):
    """
    Detect brokers acting as both heavy buyer and seller – suspicious behavior.
    Returns list of broker IDs suspected to be operator-linked.
    """
    broker_stats = defaultdict(lambda: {"buy": 0, "sell": 0})

    for row in floor_data:
        broker_stats[row["buyer"]]["buy"] += row["quantity"]
        broker_stats[row["seller"]]["sell"] += row["quantity"]

    suspicious = []
    for broker, stats in broker_stats.items():
        total = stats["buy"] + stats["sell"]
        if total == 0:
            continue
        overlap = min(stats["buy"], stats["sell"]) / total
        if overlap > 0.3:
            suspicious.append(broker)

    return suspicious
