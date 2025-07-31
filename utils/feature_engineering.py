import pandas as pd

def generate_features(records):
    df = pd.DataFrame(records)
    df["value"] = df["rate"] * df["quantity"]
    agg = df.groupby("symbol").agg({
        "rate": "mean",
        "quantity": "sum",
        "value": "sum"
    }).rename(columns={"rate": "ltp", "quantity": "total_qty", "value": "total_value"})

    agg["operator_cost"] = agg["total_value"] / agg["total_qty"]
    agg["readiness"] = (agg["ltp"] - agg["operator_cost"]) / agg["operator_cost"] * 100
    agg["readiness"] = agg["readiness"].clip(lower=0).round(2)
    agg["volatility"] = 1.5
    agg["days_to_profit"] = 5
    return agg.reset_index()
